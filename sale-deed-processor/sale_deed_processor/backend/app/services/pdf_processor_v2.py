# backend/app/services/pdf_processor_v2.py

"""
PDF Processor Version 2 - Pipeline Edition

Splits processing into 2 stages:
- Stage 1: CPU-intensive (RegFee extraction + OCR)
- Stage 2: I/O-intensive (LLM + Validation + DB save)
"""

from pathlib import Path
from typing import Optional, Dict
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.services.registration_fee_extractor import RegistrationFeeExtractor
from app.services.ocr_service import OCRService
from app.services.pymupdf_reader import PyMuPDFReader
from app.services.yolo_detector import YOLOTableDetector
from app.services.llm_service_factory import get_llm_service
from app.services.validation_service import ValidationService
from app.utils.file_handler import FileHandler
from app.models import DocumentDetail, PropertyDetail, BuyerDetail, SellerDetail, ConfirmingPartyDetail
from app.workers.pipeline_processor_v2 import Stage1Result

logger = logging.getLogger(__name__)


class PDFProcessorV2:
    """
    PDF Processor with pipeline support
    """

    def __init__(self, batch_processor=None):
        """Initialize PDF processor with all required services"""
        self.batch_processor = batch_processor
        self.reg_fee_extractor = RegistrationFeeExtractor(
            threshold_pct=0.7,
            max_misc_fee=settings.MAX_MISC_FEE,
            min_fee=settings.MIN_REGISTRATION_FEE
        )
        self.ocr_service = OCRService()
        self.pymupdf_reader = PyMuPDFReader(max_pages=30)
        self.yolo_detector = YOLOTableDetector(
            model_path=str(settings.YOLO_MODEL_PATH),
            conf_threshold=settings.YOLO_CONF_THRESHOLD
        )
        self.llm_service = get_llm_service()

        logger.info("PDF Processor V2 initialized (Pipeline mode)")

    def process_stage1_ocr(self, pdf_path: Path, db: Session) -> Stage1Result:
        """
        Stage 1: CPU-intensive processing
        - Step 1: Perform OCR with Tesseract (max 30 pages)
        - Step 2: Extract registration fee from OCR text

        Returns:
            Stage1Result with OCR text and registration fee
        """
        from app.exceptions import ProcessingStoppedException

        # Extract document ID
        document_id = FileHandler.extract_document_id(pdf_path.name)

        logger.info(f"[Stage 1] Processing: {pdf_path.name} (Document ID: {document_id})")

        try:
            # STOP CHECK
            if self.batch_processor and not self.batch_processor.is_running:
                raise ProcessingStoppedException("Stopped before Stage 1")

            # Step 1: Perform OCR - Use PyMuPDF for embedded OCR or Tesseract for traditional OCR
            pdf_images = None  # Store images for YOLO reuse
            if settings.USE_EMBEDDED_OCR:
                logger.info(f"[{document_id}] Stage1 Step1: Reading embedded OCR with PyMuPDF (max 30 pages)")
                full_ocr_text = self.pymupdf_reader.get_full_text(str(pdf_path), max_pages=30)
            else:
                logger.info(f"[{document_id}] Stage1 Step1: Performing OCR with Poppler+Tesseract (max 30 pages)")
                full_ocr_text, pdf_images = self.ocr_service.get_full_text(str(pdf_path), max_pages=30, return_images=True)

            if not full_ocr_text or len(full_ocr_text) < 100:
                raise Exception("Text extraction returned insufficient text")

            logger.info(f"[{document_id}] OCR completed: {len(full_ocr_text)} characters")

            # STOP CHECK
            if self.batch_processor and not self.batch_processor.is_running:
                raise ProcessingStoppedException("Stopped before registration fee extraction")

            # Step 2: Extract registration fee from OCR text using Registration Fee Extractor
            registration_fee = None
            logger.info(f"[{document_id}] Stage1 Step2: Extracting registration fee from OCR text")
            registration_fee = self.reg_fee_extractor.extract_from_ocr_text(full_ocr_text)

            if registration_fee:
                logger.info(f"[{document_id}] ✓ Registration Fee Extractor found fee: {registration_fee}")
            else:
                logger.warning(f"[{document_id}] Registration Fee Extractor returned null, will try LLM and YOLO later")

            return Stage1Result(
                pdf_path=pdf_path,
                document_id=document_id,
                registration_fee=registration_fee,
                new_ocr_reg_fee=None,  # Deprecated field, using registration_fee now
                ocr_text=full_ocr_text,
                status="success",
                pdf_images=pdf_images
            )

        except ProcessingStoppedException as stopped_ex:
            logger.info(f"[{document_id}] {stopped_ex.message}")
            return Stage1Result(
                pdf_path=pdf_path,
                document_id=document_id,
                registration_fee=None,
                new_ocr_reg_fee=None,
                ocr_text="",
                status="stopped",
                error=stopped_ex.message
            )

        except Exception as e:
            logger.error(f"[{document_id}] Stage 1 failed: {e}")
            return Stage1Result(
                pdf_path=pdf_path,
                document_id=document_id,
                registration_fee=None,
                new_ocr_reg_fee=None,
                ocr_text="",
                status="failed",
                error=str(e)
            )

        except ProcessingStoppedException as stopped_ex:
            logger.info(f"[{document_id}] {stopped_ex.message}")
            return Stage1Result(
                pdf_path=pdf_path,
                document_id=document_id,
                registration_fee=None,
                new_ocr_reg_fee=None,
                ocr_text="",
                status="stopped",
                error=stopped_ex.message
            )

        except Exception as e:
            logger.error(f"[{document_id}] Stage 1 failed: {e}")
            return Stage1Result(
                pdf_path=pdf_path,
                document_id=document_id,
                registration_fee=None,
                new_ocr_reg_fee=None,
                ocr_text="",
                status="failed",
                error=str(e)
            )

    def process_stage2_llm(self, stage1_result: Stage1Result, db: Session) -> Dict:
        """
        Stage 2: I/O-intensive processing
        - Extract structured data with LLM
        - Validate and clean data
        - Save to database
        - Detect YOLO table if needed

        Args:
            stage1_result: Results from Stage 1
            db: Database session

        Returns:
            Processing result dictionary
        """
        from app.exceptions import ProcessingStoppedException

        result = {
            "document_id": stage1_result.document_id,
            "status": "failed",
            "registration_fee": stage1_result.registration_fee,
            "llm_extracted": False,
            "saved_to_db": False,
            "table_detected": False,
            "error": None
        }

        try:
            document_id = stage1_result.document_id
            pdf_path = stage1_result.pdf_path
            registration_fee = stage1_result.registration_fee
            new_ocr_reg_fee = stage1_result.new_ocr_reg_fee

            logger.info(f"[Stage 2] Processing: {document_id}")

            # STOP CHECK
            if self.batch_processor and not self.batch_processor.is_running:
                raise ProcessingStoppedException("Stopped before LLM")

            # Step 3: Extract structured data with LLM
            logger.info(f"[{document_id}] Stage2: Extracting with LLM")
            extracted_data = self.llm_service.extract_structured_data(stage1_result.ocr_text)

            if not extracted_data:
                raise Exception("LLM failed to extract structured data")

            result["llm_extracted"] = True
            logger.info(f"[{document_id}] LLM extraction successful")
            
            # TEMPORARY DEBUG: Print complete JSON response from LLM
            import json
            logger.info(f"[{document_id}] ========== COMPLETE LLM JSON RESPONSE ==========")
            logger.info(json.dumps(extracted_data, indent=2, ensure_ascii=False))
            logger.info(f"[{document_id}] ================================================")

            # DEBUG: Log extracted property details
            if "property_details" in extracted_data:
                logger.info(f"[{document_id}] DEBUG - LLM Extracted Property Details:")
                logger.info(f"  schedule_b_area: {extracted_data['property_details'].get('schedule_b_area')}")
                logger.info(f"  schedule_c_property_name: {extracted_data['property_details'].get('schedule_c_property_name')}")
                logger.info(f"  schedule_c_property_address: {extracted_data['property_details'].get('schedule_c_property_address')}")
                logger.info(f"  schedule_c_property_area: {extracted_data['property_details'].get('schedule_c_property_area')}")
                logger.info(f"  paid_in_cash_mode: {extracted_data['property_details'].get('paid_in_cash_mode')}")

            # STOP CHECK
            if self.batch_processor and not self.batch_processor.is_running:
                raise ProcessingStoppedException("Stopped before validation")

            # Step 4: Validate and clean data
            logger.info(f"[{document_id}] Stage2: Validating data")
            cleaned_data = ValidationService.validate_and_clean_data(extracted_data)

            # DEBUG: Log cleaned property details after validation
            if "property_details" in cleaned_data:
                logger.info(f"[{document_id}] DEBUG - Cleaned Property Details (after validation):")
                logger.info(f"  schedule_b_area: {cleaned_data['property_details'].get('schedule_b_area')}")
                logger.info(f"  schedule_c_property_name: {cleaned_data['property_details'].get('schedule_c_property_name')}")
                logger.info(f"  schedule_c_property_address: {cleaned_data['property_details'].get('schedule_c_property_address')}")
                logger.info(f"  schedule_c_property_area: {cleaned_data['property_details'].get('schedule_c_property_area')}")
                logger.info(f"  paid_in_cash_mode: {cleaned_data['property_details'].get('paid_in_cash_mode')}")


            # NEW REGISTRATION FEE PRIORITY LOGIC:
            # Priority 1: Registration Fee Extractor (from Stage 1 OCR text) - FINAL if found
            # Priority 2: YOLO+Vision - if extractor returned null
            # Priority 3: LLM extraction - if both above returned null

            final_registration_fee = None
            table_detected = False  # Initialize to avoid UnboundLocalError
            llm_registration_fee = cleaned_data["property_details"].get("registration_fee")

            # Priority 1: Registration Fee Extractor (from Stage 1)
            if registration_fee:
                final_registration_fee = registration_fee
                cleaned_data["property_details"]["registration_fee"] = registration_fee
                cleaned_data["property_details"]["guidance_value"] = \
                    ValidationService.calculate_guidance_value(registration_fee)
                logger.info(f"[{document_id}] ✓ Using Registration Fee Extractor (Priority 1 - FINAL): {registration_fee}")

            # Priority 2: YOLO+Vision (if extractor didn't find it)
            else:
                logger.info(f"[{document_id}] Registration Fee Extractor returned null, trying YOLO+Vision (Priority 2)")
                
                # STOP CHECK
                if self.batch_processor and not self.batch_processor.is_running:
                    raise ProcessingStoppedException("Stopped before YOLO")

                # Reuse images from Stage 1 OCR if available, otherwise convert PDF
                table_image_path, table_detected = self._detect_and_save_table(pdf_path, document_id, stage1_result.pdf_images)
                result["table_detected"] = table_detected

                if table_detected and table_image_path:
                    logger.info(f"[{document_id}] ✓ YOLO table detected, sending to VLM")

                    # Send table image to VLM (Priority 2)
                    try:
                        from app.services.gemini_vision_service import GeminiVisionService
                        vision_service = GeminiVisionService()
                        vlm_registration_fee = vision_service.extract_registration_fee(str(table_image_path))

                        if vlm_registration_fee:
                            logger.info(f"[{document_id}] ✓ VLM extracted registration fee (Priority 2): {vlm_registration_fee}")
                            final_registration_fee = vlm_registration_fee
                            cleaned_data["property_details"]["registration_fee"] = vlm_registration_fee
                            cleaned_data["property_details"]["guidance_value"] = \
                                ValidationService.calculate_guidance_value(vlm_registration_fee)
                        else:
                            logger.warning(f"[{document_id}] VLM could not extract registration fee from table")
                    except Exception as vlm_error:
                        logger.error(f"[{document_id}] VLM extraction error: {vlm_error}")
                else:
                    logger.warning(f"[{document_id}] YOLO failed to detect table")

                # Priority 3: LLM registration fee (fallback if both extractor and YOLO failed)
                if not final_registration_fee and llm_registration_fee:
                    logger.info(f"[{document_id}] YOLO+Vision returned null, trying LLM (Priority 3)")
                    try:
                        llm_reg_fee_value = float(llm_registration_fee) if isinstance(llm_registration_fee, str) else llm_registration_fee
                        cleaned_data["property_details"]["registration_fee"] = llm_reg_fee_value
                        cleaned_data["property_details"]["guidance_value"] = \
                            ValidationService.calculate_guidance_value(llm_reg_fee_value)
                        final_registration_fee = llm_reg_fee_value
                        logger.info(f"[{document_id}] ✓ Using LLM registration fee (Priority 3): {llm_reg_fee_value}")
                    except (ValueError, TypeError) as e:
                        logger.warning(f"[{document_id}] LLM registration fee invalid: {e}")
                        final_registration_fee = None

            # STEP 4.1: Transliterate Kannada → Human-readable English
            from app.services.transliteration import transliterate_json_fields
            cleaned_data = transliterate_json_fields(cleaned_data)

            # STOP CHECK
            if self.batch_processor and not self.batch_processor.is_running:
                raise ProcessingStoppedException("Stopped before DB save")

            # Step 5: Save to database
            logger.info(f"[{document_id}] Stage2: Saving to database")
            try:
                self._save_to_database(document_id, cleaned_data, new_ocr_reg_fee, db)
                result["saved_to_db"] = True
                logger.info(f"[{document_id}] Successfully saved to database")
            except Exception as db_error:
                logger.error(f"[{document_id}] Database save failed: {db_error}")
                raise Exception(f"Database save failed: {db_error}")

            # Update database with final registration fee if YOLO found it
            if final_registration_fee and table_detected:
                try:
                    from app.models import PropertyDetail
                    prop = db.query(PropertyDetail).filter(PropertyDetail.document_id == document_id).first()
                    if prop:
                        # Format and save
                        if final_registration_fee == int(final_registration_fee):
                            prop.registration_fee = str(int(final_registration_fee))
                        else:
                            prop.registration_fee = f"{final_registration_fee:.2f}"

                        # Calculate and save guidance value
                        guidance_value = ValidationService.calculate_guidance_value(final_registration_fee)
                        if guidance_value == int(guidance_value):
                            prop.guidance_value = str(int(guidance_value))
                        else:
                            prop.guidance_value = f"{guidance_value:.2f}"

                        db.commit()
                        logger.info(f"[{document_id}] ✓ Updated DB with registration fee: {prop.registration_fee}")
                except Exception as update_error:
                    logger.error(f"[{document_id}] Failed to update registration fee in DB: {update_error}")

            # Log final result
            if not final_registration_fee:
                logger.warning(f"[{document_id}] ⚠ No registration fee available from any source (Extractor, YOLO+VLM, LLM)")
            else:
                result["registration_fee"] = final_registration_fee

            # Step 7: Move to processed folder
            result["status"] = "success"
            FileHandler.move_file(pdf_path, settings.PROCESSED_DIR)
            logger.info(f"[{document_id}] Processing completed successfully")

        except ProcessingStoppedException as stopped_ex:
            logger.info(f"[{result['document_id']}] {stopped_ex.message}")
            result["status"] = "stopped"
            result["error"] = stopped_ex.message

        except Exception as e:
            logger.error(f"[{result['document_id']}] Stage 2 failed: {e}")
            result["error"] = str(e)
            result["status"] = "failed"

            # Move to failed folder
            if stage1_result.pdf_path.exists():
                FileHandler.move_file(stage1_result.pdf_path, settings.FAILED_DIR)

        return result

    def _detect_and_save_table(self, pdf_path: Path, document_id: str, cached_images=None):
        """
        Detect table with YOLO and save cropped table (reuses OCR images if available)

        Returns:
            tuple: (table_image_path, table_detected) - Path to saved table image and detection status
        """
        try:
            # Reuse images from OCR if available, otherwise convert PDF
            if cached_images:
                images = cached_images
                logger.info(f"[{document_id}] Reusing {len(images)} images from OCR stage")
            else:
                images = self.ocr_service.pdf_to_images(str(pdf_path), max_pages=30)
                logger.info(f"[{document_id}] Converted PDF to {len(images)} images (max 30)")

            for page_num, image in enumerate(images, start=1):
                temp_image_path = settings.LEFT_OVER_REG_FEE_DIR / f"temp_{document_id}page{page_num}.png"
                image.save(temp_image_path)

                output_image_path = settings.LEFT_OVER_REG_FEE_DIR / f"{document_id}_table.png"

                cropped_table = self.yolo_detector.detect_and_crop(
                    str(temp_image_path),
                    str(output_image_path)
                )

                if temp_image_path.exists():
                    temp_image_path.unlink()

                if cropped_table is not None:
                    logger.info(f"[{document_id}] Table detected on page {page_num}")
                    return output_image_path, True

            logger.warning(f"[{document_id}] No table detected in any page")
            return None, False

        except Exception as e:
            logger.error(f"[{document_id}] YOLO detection error: {e}")
            return None, False

    def _save_to_database(self, document_id: str, data: Dict, new_ocr_reg_fee: Optional[float], db: Session):
        """Save extracted data to database"""
        try:
            # Create or update document details
            doc_data = data.get("document_details", {})

            doc = db.query(DocumentDetail).filter(DocumentDetail.document_id == document_id).first()
            if not doc:
                doc = DocumentDetail(
                    document_id=document_id,
                    transaction_date=doc_data.get("transaction_date"),
                    registration_office=doc_data.get("registration_office")
                )
                db.add(doc)
            else:
                doc.transaction_date = doc_data.get("transaction_date")
                doc.registration_office = doc_data.get("registration_office")
                doc.updated_at = datetime.utcnow()

            db.flush()

            # Create or update property details
            prop_data = data.get("property_details", {})

            # DEBUG: Log property data being saved to DB
            logger.info(f"[{document_id}] DEBUG - Property data being saved to DB:")
            logger.info(f"  schedule_b_area: {prop_data.get('schedule_b_area')}")
            logger.info(f"  schedule_c_property_name: {prop_data.get('schedule_c_property_name')}")
            logger.info(f"  schedule_c_property_address: {prop_data.get('schedule_c_property_address')}")
            logger.info(f"  schedule_c_property_area: {prop_data.get('schedule_c_property_area')}")
            logger.info(f"  paid_in_cash_mode: {prop_data.get('paid_in_cash_mode')}")

            prop = db.query(PropertyDetail).filter(PropertyDetail.document_id == document_id).first()
            if not prop:
                prop = PropertyDetail(document_id=document_id)
                db.add(prop)

            prop.schedule_b_area = prop_data.get("schedule_b_area")
            prop.schedule_c_property_name = prop_data.get("schedule_c_property_name")
            prop.schedule_c_property_address = prop_data.get("schedule_c_property_address")
            prop.schedule_c_property_area = prop_data.get("schedule_c_property_area")
            prop.paid_in_cash_mode = prop_data.get("paid_in_cash_mode")
            prop.pincode = prop_data.get("pincode")
            prop.state = prop_data.get("state")
            prop.sale_consideration = prop_data.get("sale_consideration")
            prop.stamp_duty_fee = prop_data.get("stamp_duty_fee")

            # Format registration_fee as string
            reg_fee_value = prop_data.get("registration_fee")
            if reg_fee_value is not None:
                if isinstance(reg_fee_value, float):
                    if reg_fee_value == int(reg_fee_value):
                        prop.registration_fee = str(int(reg_fee_value))
                    else:
                        prop.registration_fee = f"{reg_fee_value:.2f}"
                else:
                    prop.registration_fee = str(reg_fee_value)
            else:
                prop.registration_fee = None

            # Format new_ocr_reg_fee as string (from OCR text extraction)
            if new_ocr_reg_fee is not None:
                if isinstance(new_ocr_reg_fee, float):
                    if new_ocr_reg_fee == int(new_ocr_reg_fee):
                        prop.new_ocr_reg_fee = str(int(new_ocr_reg_fee))
                    else:
                        prop.new_ocr_reg_fee = f"{new_ocr_reg_fee:.2f}"
                else:
                    prop.new_ocr_reg_fee = str(new_ocr_reg_fee)
            else:
                prop.new_ocr_reg_fee = None

            # Format guidance_value as string
            guidance_value = prop_data.get("guidance_value")
            if guidance_value is not None:
                if isinstance(guidance_value, float):
                    if guidance_value == int(guidance_value):
                        prop.guidance_value = str(int(guidance_value))
                    else:
                        prop.guidance_value = f"{guidance_value:.2f}"
                else:
                    prop.guidance_value = str(guidance_value)
            else:
                prop.guidance_value = None

            db.flush()

            # Delete existing buyers, sellers, and confirming parties
            db.query(BuyerDetail).filter(BuyerDetail.document_id == document_id).delete()
            db.query(SellerDetail).filter(SellerDetail.document_id == document_id).delete()
            db.query(ConfirmingPartyDetail).filter(ConfirmingPartyDetail.document_id == document_id).delete()

            # Insert buyers
            buyers = data.get("buyer_details", [])
            for buyer_data in buyers:
                buyer = BuyerDetail(
                    document_id=document_id,
                    name=buyer_data.get("name"),
                    gender=buyer_data.get("gender"),
                    father_name=buyer_data.get("father_name"),
                    date_of_birth=buyer_data.get("date_of_birth"),
                    aadhaar_number=buyer_data.get("aadhaar_number"),
                    pan_card_number=buyer_data.get("pan_card_number"),
                    address=buyer_data.get("address"),
                    pincode=buyer_data.get("pincode"),
                    state=buyer_data.get("state"),
                    phone_number=buyer_data.get("phone_number"),
                    secondary_phone_number=buyer_data.get("secondary_phone_number"),
                    email=buyer_data.get("email")
                )
                db.add(buyer)

            # Insert sellers
            sellers = data.get("seller_details", [])
            for seller_data in sellers:
                seller = SellerDetail(
                    document_id=document_id,
                    name=seller_data.get("name"),
                    gender=seller_data.get("gender"),
                    father_name=seller_data.get("father_name"),
                    date_of_birth=seller_data.get("date_of_birth"),
                    aadhaar_number=seller_data.get("aadhaar_number"),
                    pan_card_number=seller_data.get("pan_card_number"),
                    address=seller_data.get("address"),
                    pincode=seller_data.get("pincode"),
                    state=seller_data.get("state"),
                    phone_number=seller_data.get("phone_number"),
                    secondary_phone_number=seller_data.get("secondary_phone_number"),
                    email=seller_data.get("email"),
                    property_share=seller_data.get("property_share")
                )
                db.add(seller)

            # Insert confirming parties
            confirming_parties = data.get("confirming_party_details", [])
            for confirming_data in confirming_parties:
                confirming_party = ConfirmingPartyDetail(
                    document_id=document_id,
                    name=confirming_data.get("name"),
                    gender=confirming_data.get("gender"),
                    father_name=confirming_data.get("father_name"),
                    date_of_birth=confirming_data.get("date_of_birth"),
                    aadhaar_number=confirming_data.get("aadhaar_number"),
                    pan_card_number=confirming_data.get("pan_card_number"),
                    address=confirming_data.get("address"),
                    pincode=confirming_data.get("pincode"),
                    state=confirming_data.get("state"),
                    phone_number=confirming_data.get("phone_number"),
                    secondary_phone_number=confirming_data.get("secondary_phone_number"),
                    email=confirming_data.get("email")
                )
                db.add(confirming_party)

            db.commit()
            logger.info(f"[{document_id}] Saved: {len(buyers)} buyers, {len(sellers)} sellers, {len(confirming_parties)} confirming parties")

        except Exception as e:
            db.rollback()
            logger.error(f"[{document_id}] Database save error: {e}")
            raise