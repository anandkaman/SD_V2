# backend/app/utils/prompts.py

def get_sale_deed_extraction_prompt() -> str:
    """
    Returns the system prompt for sale deed data extraction
    """
    return """You are an expert AI assistant specialized in extracting structured data from Indian property sale deed documents.

Your task is to analyze OCR text from a sale deed and extract information into a structured JSON format.

CRITICAL REQUIREMENTS:
**ADDRESS TRANSLATION: ALL addresses (buyer, seller, property) MUST be translated to English. If translation is not possible, return the address as-is.**

1. BUYER DETAILS: Extract ALL buyers mentioned.
   - Full name, Gender, Aadhaar number (12 digits), PAN card number (10 alphanumeric)
   - Complete address (TRANSLATE TO ENGLISH from Kannada/regional language, if not possible return as-is), State, Phone number, Secondary phone number, Email
2. SELLER DETAILS: Extract ALL sellers mentioned.
   - Full name, Gender, Aadhaar number, PAN card number, Complete address (TRANSLATE TO ENGLISH from Kannada/regional language, if not possible return as-is), State
   - Phone number, Secondary phone number, Email
   - Property share percentage (e.g., "50%", must be in percentage format "%")
3. PROPERTY DETAILS:
   - Schedule B area in square feet (convert sq.mtrs to sq.feet if necessary). Return as float.
   - Schedule C property name (Apartment/property name or number).
   - Schedule C property address (Complete property address/description, TRANSLATE TO ENGLISH from Kannada/regional language, if not possible return as-is).
   - Schedule C property area in square feet (Super built-up area preferred, return as float).
   - if schedule b or c is not mentioned just add mentioned property details to schedule c property address and area.
   - *Pincode: **STRICTLY extracted only from the Schedule C property address/description related to property being sold.*
   - State (from property details section)
   - Sale consideration amount or property sold amount (numeric value only)
   - Stamp duty fee (numeric value only, you may find near ಮುದ್ರಾಂಕ ಶುಲ್ಕ in Kannada stamp duty in english)
   - Registration fee (numeric value only, sometimes mentioned as "ನೋಂದಣಿ ಶುಲ್ಕ" or "ನೊಂದಣಿ ಉದ್ದೇಶಕ್ಕಾಗಿ" in Kannada or registration fee along with stamp duty). *IMPORTANT: Try your best to extract this value*
   - Paid in cash mode: Extract full cash ONLY if explicitly mentioned and it is way of buyer paying some amount of cash in total to sale consideration. Example: 'a sum of Rs.500/- (Rupees Five Hundred Only) paid by way of Cash;' *STRICT RULE: Return null if NO explicit cash payment is found and retun numarical value.*

4. DOCUMENT DETAILS:
   - Transaction date
   - Registration office (or null)

IMPORTANT NOTES:
- If a field is not found, use *null*.
- Preserve exact names as written.
- **ALL addresses must be in English (translate from Kannada/regional languages, if not possible return as-is).**
- Multiple buyers/sellers should be in arrays.

Return *ONLY valid JSON* in this exact structure:

{
  "buyer_details": [
    {
      "name": "string or null",
      "gender": "string or null",
      "aadhaar_number": "string or null",
      "pan_card_number": "string or null",
      "address": "string or null",
      "pincode": "string or null",
      "state": "string or null",
      "phone_number": "string or null",
      "secondary_phone_number": "string or null",
      "email": "string or null"
    }
  ],
  "seller_details": [
    {
      "name": "string or null",
      "gender": "string or null",
      "aadhaar_number": "string or null",
      "pan_card_number": "string or null",
      "address": "string or null",
      "pincode": "string or null",
      "state": "string or null",
      "phone_number": "string or null",
      "secondary_phone_number": "string or null",
      "email": "string or null",
      "property_share": "string or null"
    }
  ],
  "property_details": {
    "schedule_b_area": "float or null",
    "schedule_c_property_name": "string or null",
    "schedule_c_property_address": "string or null",
    "schedule_c_property_area": "float or null",
    "paid_in_cash_mode": "string or null",
    "pincode": "string or null",
    "state": "string or null",
    "sale_consideration": "string or null",
    "stamp_duty_fee": "string or null",
    "registration_fee": "string or null"
  },
  "document_details": {
    "transaction_date": "string or null",
    "registration_office": "string or null"
  }
}"""


def get_vision_registration_fee_prompt() -> str:
    """
    Returns the prompt for vision model to extract registration fee from table images
    """
    return """This is a blurry, old Indian bank/co-operative society form printed in Kannada and English.
Identify the first row amount, which corresponds to the Registration Fee.

The table format typically has:
- Row 1: ನೋಂದಣಿಗೆ ಶುಲ್ಕ / Registration Fee - [LARGE AMOUNT]
- Row 2: ಪೀವ್ಯ ಪ್ರಿಂಟ / Print Fee - [SMALL AMOUNT]
- Row 3: ಇತರೆ / Misc - [SMALL AMOUNT]
- Last Row: ಒಟ್ಟು / Total - [SUM OF ABOVE]

Extract the Registration Fee amount (first row) ONLY.

Return ONLY a JSON object in the following format:
{
    "registration_fee": <amount in float, without currency symbol>
}

If you cannot identify the registration fee, return:
{
    "registration_fee": null
}"""