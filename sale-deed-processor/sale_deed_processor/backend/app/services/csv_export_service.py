# CSV Export Service for 42-column format
# This file handles the CSV export functionality with the specific column mapping

import csv
import io
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.models import DocumentDetail, BuyerDetail, SellerDetail, ConfirmingPartyDetail

def generate_csv_export(
    db: Session,
    batch_ids: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> io.StringIO:
    """
    Generate CSV export with 42 columns as per specification
    
    Column Mapping:
    1. Report Serial Number - Increments for each new document_id
    2. Original Report Serial Number - Empty
    3. Transaction Date - transaction_date from document_details
    4. Transaction Identity - document_id
    5. Transaction Type - Empty
    6. Transaction Amount - sale_consideration from property_details
    7. Property Type - Empty
    8. Whether property is within municipal limits - Empty
    9. Property Address - schedule_c_property_address
    10. City / Town - schedule_c_property_address
    11. Postal Code - pincode from property_details
    12. State Code - state from property_details
    13. Country Code - "IN"
    14. Stamp Value - registration_fee from property_details
    15. Remarks - Empty
    16. Transaction Relation (PC) - "S" for seller, "B" for buyer, "C" for confirming party
    17. Transaction Amount related to the person (PC) - sale_consideration
    18-42. Person-specific details (name, gender, father_name, etc.)
    """
    
    # Query with eager loading
    query = db.query(DocumentDetail).options(
        joinedload(DocumentDetail.property_details),
        joinedload(DocumentDetail.buyers),
        joinedload(DocumentDetail.sellers),
        joinedload(DocumentDetail.confirming_parties)
    )
    
    # Apply filters
    if batch_ids:
        batch_list = batch_ids.split(',')
        query = query.filter(DocumentDetail.batch_id.in_(batch_list))
    
    if start_date:
        query = query.filter(DocumentDetail.transaction_date >= start_date)
    
    if end_date:
        query = query.filter(DocumentDetail.transaction_date <= end_date)
    
    documents = query.all()
    
    # Create CSV in memory
    output = io.StringIO()
    
    # Define 42 column headers
    headers = [
        "Report Serial Number",
        "Original Report Serial Number",
        "Transaction Date",
        "Transaction Identity",
        "Transaction Type",
        "Transaction Amount",
        "Property Type",
        "Whether property is within municipal limits",
        "Property Address",
        "City / Town",
        "Postal Code",
        "State Code",
        "Country Code",
        "Stamp Value",
        "Remarks",
        "Transaction Relation (PC)",
        "Transaction Amount related to the person (PC)",
        "Person Name (PC)",
        "Person Type (PC)",
        "Gender (PC)",
        "Father's Name (PC)",
        "PAN (PC)",
        "Aadhaar Number (PC)",
        "Form 60 Acknowledgement (PC)",
        "Identification Type (PC)",
        "Identification Number (PC)",
        "Date of Birth/ Incorporation (PC)",
        "Nationality/Country of Incorporation (PC)",
        "Address Type (PC-L)",
        "Address (PC-L)",
        "City/Town (PC-L)",
        "Pin Code (PC-L)",
        "State (PC-L)",
        "Country (PC-L)",
        "Primary STD Code (PC)",
        "Primary Phone Number (PC)",
        "Primary Mobile Number (PC)",
        "Secondary STD Code (PC)",
        "Secondary Phone Number (PC)",
        "Secondary Mobile Number (PC)",
        "Email (PC)",
        "Person Details Remarks (PC)"
    ]
    
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    
    report_serial = 1
    
    for doc in documents:
        prop = doc.property_details
        
        # Base row data (same for all persons in this document)
        base_data = {
            "Report Serial Number": report_serial,
            "Original Report Serial Number": "",
            "Transaction Date": doc.transaction_date if doc.transaction_date else "",
            "Transaction Identity": doc.document_id,
            "Transaction Type": "",
            "Transaction Amount": prop.sale_consideration if prop and prop.sale_consideration else "",
            "Property Type": "",
            "Whether property is within municipal limits": "",
            "Property Address": prop.schedule_c_property_address if prop and prop.schedule_c_property_address else "",
            "City / Town": prop.schedule_c_property_address if prop and prop.schedule_c_property_address else "",
            "Postal Code": prop.pincode if prop and prop.pincode else "",
            "State Code": prop.state if prop and prop.state else "",
            "Country Code": "IN",
            "Stamp Value": prop.registration_fee if prop and prop.registration_fee else "",
            "Remarks": prop.remarks if prop and prop.remarks else "",  # NEW: Map from property_details
            "Transaction Amount related to the person (PC)": prop.sale_consideration if prop and prop.sale_consideration else ""
        }
        
        # Add sellers (S)
        for seller in doc.sellers:
            row = base_data.copy()
            row.update({
                "Transaction Relation (PC)": "S",
                "Person Name (PC)": seller.name if seller.name else "",
                "Person Type (PC)": "",
                "Gender (PC)": seller.gender if seller.gender else "",
                "Father's Name (PC)": seller.father_name if seller.father_name else "",
                "PAN (PC)": seller.pan_card_number if seller.pan_card_number else "",
                "Aadhaar Number (PC)": seller.aadhaar_number if seller.aadhaar_number else "",
                "Form 60 Acknowledgement (PC)": "",
                "Identification Type (PC)": "",
                "Identification Number (PC)": "",
                "Date of Birth/ Incorporation (PC)": seller.date_of_birth.strftime('%Y-%m-%d') if seller.date_of_birth else "",
                "Nationality/Country of Incorporation (PC)": "IN",
                "Address Type (PC-L)": "",
                "Address (PC-L)": seller.address if seller.address else "",
                "City/Town (PC-L)": seller.address if seller.address else "",
                "Pin Code (PC-L)": seller.pincode if seller.pincode else "",
                "State (PC-L)": seller.state if seller.state else "",
                "Country (PC-L)": "IN",
                "Primary STD Code (PC)": "",
                "Primary Phone Number (PC)": "",
                "Primary Mobile Number (PC)": seller.phone_number if seller.phone_number else "",
                "Secondary STD Code (PC)": "",
                "Secondary Phone Number (PC)": "",
                "Secondary Mobile Number (PC)": seller.secondary_phone_number if seller.secondary_phone_number else "",
                "Email (PC)": seller.email if seller.email else "",
                "Person Details Remarks (PC)": ""
            })
            writer.writerow(row)
        
        # Add buyers (B)
        for buyer in doc.buyers:
            row = base_data.copy()
            row.update({
                "Transaction Relation (PC)": "B",
                "Person Name (PC)": buyer.name if buyer.name else "",
                "Person Type (PC)": "",
                "Gender (PC)": buyer.gender if buyer.gender else "",
                "Father's Name (PC)": buyer.father_name if buyer.father_name else "",
                "PAN (PC)": buyer.pan_card_number if buyer.pan_card_number else "",
                "Aadhaar Number (PC)": buyer.aadhaar_number if buyer.aadhaar_number else "",
                "Form 60 Acknowledgement (PC)": "",
                "Identification Type (PC)": "",
                "Identification Number (PC)": "",
                "Date of Birth/ Incorporation (PC)": buyer.date_of_birth.strftime('%Y-%m-%d') if buyer.date_of_birth else "",
                "Nationality/Country of Incorporation (PC)": "IN",
                "Address Type (PC-L)": "",
                "Address (PC-L)": buyer.address if buyer.address else "",
                "City/Town (PC-L)": buyer.address if buyer.address else "",
                "Pin Code (PC-L)": buyer.pincode if buyer.pincode else "",
                "State (PC-L)": buyer.state if buyer.state else "",
                "Country (PC-L)": "IN",
                "Primary STD Code (PC)": "",
                "Primary Phone Number (PC)": "",
                "Primary Mobile Number (PC)": buyer.phone_number if buyer.phone_number else "",
                "Secondary STD Code (PC)": "",
                "Secondary Phone Number (PC)": "",
                "Secondary Mobile Number (PC)": buyer.secondary_phone_number if buyer.secondary_phone_number else "",
                "Email (PC)": buyer.email if buyer.email else "",
                "Person Details Remarks (PC)": ""
            })
            writer.writerow(row)
        
        # Add confirming parties (C)
        for confirming in doc.confirming_parties:
            row = base_data.copy()
            row.update({
                "Transaction Relation (PC)": "C",
                "Person Name (PC)": confirming.name if confirming.name else "",
                "Person Type (PC)": "",
                "Gender (PC)": confirming.gender if confirming.gender else "",
                "Father's Name (PC)": confirming.father_name if confirming.father_name else "",
                "PAN (PC)": confirming.pan_card_number if confirming.pan_card_number else "",
                "Aadhaar Number (PC)": confirming.aadhaar_number if confirming.aadhaar_number else "",
                "Form 60 Acknowledgement (PC)": "",
                "Identification Type (PC)": "",
                "Identification Number (PC)": "",
                "Date of Birth/ Incorporation (PC)": confirming.date_of_birth.strftime('%Y-%m-%d') if confirming.date_of_birth else "",
                "Nationality/Country of Incorporation (PC)": "IN",
                "Address Type (PC-L)": "",
                "Address (PC-L)": confirming.address if confirming.address else "",
                "City/Town (PC-L)": confirming.address if confirming.address else "",
                "Pin Code (PC-L)": confirming.pincode if confirming.pincode else "",
                "State (PC-L)": confirming.state if confirming.state else "",
                "Country (PC-L)": "IN",
                "Primary STD Code (PC)": "",
                "Primary Phone Number (PC)": "",
                "Primary Mobile Number (PC)": confirming.phone_number if confirming.phone_number else "",
                "Secondary STD Code (PC)": "",
                "Secondary Phone Number (PC)": "",
                "Secondary Mobile Number (PC)": confirming.secondary_phone_number if confirming.secondary_phone_number else "",
                "Email (PC)": confirming.email if confirming.email else "",
                "Person Details Remarks (PC)": ""
            })
            writer.writerow(row)
        
        report_serial += 1
    
    output.seek(0)
    return output
