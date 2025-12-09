✅ AUCTION MODEL FIELD VERIFICATION
=====================================

DATABASE MODEL (models_marketplace.py - Line 216)
================================================

Column Name          | Type      | Default          | Nullable | Description
--------------------|-----------|------------------|----------|------------------------------------------
id                   | String(36)| UUID             | NO       | Primary Key
seller_id (FK)       | String(36)| -                | NO       | References farmers.id
crop_name            | String    | -                | NO       | Crop type (Wheat, Sunflower, etc)
quantity_quintal     | Float     | -                | NO       | Quantity in quintals
base_price           | Float     | -                | NO       | Government mandi reference price
min_bid_price        | Float     | -                | NO       | Farmer's minimum acceptable bid
current_highest_bid  | Float     | 0                | YES      | Current highest bid amount
start_time           | DateTime  | utcnow()         | YES      | Auction start time
end_time             | DateTime  | -                | NO       | Auction end time
status               | String(20)| "live"           | YES      | live/ended/sold/cancelled
winning_buyer_id (FK)| String(36)| -                | YES      | References buyers.id
final_price          | Float     | -                | YES      | Final sold price
photo1_path          | String    | -                | YES      | Primary photo path
photo2_path          | String    | -                | YES      | Secondary photo path
photo3_path          | String    | -                | YES      | Tertiary photo path
description          | Text      | -                | YES      | Detailed crop description
location             | String    | -                | YES      | Auction location
created_at           | DateTime  | utcnow()         | YES      | Creation timestamp
updated_at           | DateTime  | utcnow()         | YES      | Last update timestamp


CREATE AUCTION FUNCTION (bidding.py - Line 111)
===============================================

✅ FORM INPUT PARSING:
  - crop_name ✅ (from form, stripped)
  - quantity ✅ (from form as quantity_str, converted to float)
  - min_bid_price ✅ (from form as min_bid_price_str, converted to float)
  - duration_hours ✅ (from form as duration_hours_str, converted to int)
  - location ✅ (from form, stripped)
  - description ✅ (from form, stripped)

✅ AUTO-GENERATED:
  - id ✅ (uuid.uuid4())
  - base_price ✅ (fetched from get_base_price() function)
  - start_time ✅ (defaults to utcnow() in model)
  - created_at ✅ (explicitly set to utcnow())
  - updated_at ✅ (explicitly set to utcnow())

✅ COMPUTED:
  - end_time ✅ (utcnow() + timedelta(hours=duration_hours))
  - status ✅ (hardcoded to 'live')

✅ PHOTO HANDLING:
  - photo1_path ✅ (from request.files['photo1'])
  - photo2_path ✅ (from request.files['photo2'], optional)
  - photo3_path ✅ (from request.files['photo3'], optional)
  - Validation: ✅ At least one photo required
  - Storage: ✅ UUID-prefixed filenames in static/auction_photos/

✅ RELATIONSHIPS:
  - seller_id ✅ (from session['farmer_id_verified'])

❌ NOT SET (defaults in model):
  - winning_buyer_id ❌ (defaults to None, set later when auction sold)
  - final_price ❌ (defaults to None, set when auction sold)
  - current_highest_bid ❌ (defaults to 0, updated when bids placed)


TO_DICT() METHOD (models_marketplace.py - Line 260)
===================================================

Output Field         | Source Field           | Type    | Purpose
--------------------|------------------------|---------|---------------------------
id                   | id                     | String  | Auction ID
crop_name            | crop_name              | String  | Crop type
quantity             | quantity_quintal       | Float   | Quantity in Q
base_price           | base_price             | Float   | Mandi price
min_bid              | min_bid_price          | Float   | Min acceptable bid
min_bid_price        | min_bid_price          | Float   | (duplicate)
current_bid          | current_highest_bid    | Float   | (alias)
current_highest_bid  | current_highest_bid    | Float   | Highest bid received
time_left            | get_time_remaining()   | Int     | Seconds remaining
status               | status                 | String  | live/ended/sold/cancelled
bids_count           | len(bids_list)         | Int     | Number of bids
bidders_count        | set(buyer_ids)         | Int     | Unique bidders
avg_bid              | sum/count bids         | Float   | Average bid amount
winning_buyer        | winning_buyer_id       | String  | Winning buyer ID
final_price          | final_price            | Float   | Final sold price
location             | location               | String  | Location
description          | description            | String  | Description
photo1               | photo1_path            | String  | (alias)
photo1_path          | photo1_path            | String  | Photo 1 path
photo2_path          | photo2_path            | String  | Photo 2 path
photo3_path          | photo3_path            | String  | Photo 3 path
start_time           | start_time             | ISO-8601| Auction start
end_time             | end_time               | ISO-8601| Auction end
created_at           | created_at             | ISO-8601| Created date
seller_id            | seller_id              | String  | Seller farmer ID


VALIDATION CHECKS
=================

✅ crop_name:     Required, stripped, non-empty check
✅ quantity:      Required, positive number (> 0)
✅ min_bid_price: Required, positive number (> 0)
✅ duration_hours: Required, positive number (> 0), max 72 hours recommended
✅ location:      Required, stripped
✅ description:   Optional
✅ photo1:        Required (at least one photo must be uploaded)
✅ photo2/3:      Optional
✅ file_size:     Max 5MB per file (checked by allowed_file())
✅ file_type:     Only PNG, JPG, JPEG, GIF allowed


CONCLUSION
==========

✅ ALL FIELDS ARE CORRECT AND PROPERLY MAPPED
✅ CREATE AUCTION FUNCTION USES CORRECT FIELD NAMES
✅ TO_DICT() METHOD INCLUDES ALL NECESSARY FIELDS
✅ VALIDATION IS COMPREHENSIVE
✅ PHOTO HANDLING IS SECURE

The Auction model and bidding.py create_auction function are fully synchronized!

