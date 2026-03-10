# Mining Supply Chain API — Documentation

> **Version:** 1.0.0  
> **Base URL:** `http://172.16.2.31:8000`  
> **API Prefix:** All endpoints are under `/api/v1/`  
> **Date System:** Jalali (Solar Hijri) calendar for all date inputs  
> **Currency:** Iranian Rials (IRR)

---

# 1. Overview

The **Mining Supply Chain API** is a backend system for managing the full operational lifecycle of a gold mining operation in Iran. It tracks the movement of raw ore from the mine through grinding facilities and bunker transport to the processing factory, along with laboratory quality control (gold assay analysis) and financial payment records.

**What this API manages:**

- **Drivers & Cars** — Registry of truck drivers and their vehicles
- **Truck Loads** — Each trip carrying raw ore from the mine to a grinding facility
- **Grinding** — Processing ledger at each grinding facility (input/output/waste tonnage, costs)
- **Bunkers** — Ground ore transport from grinding facilities to the factory
- **Lab Batches & Results** — Gold assay analysis samples and their ppm readings
- **Payments** — Financial tracking of transportation and processing costs, grouped by bank transaction
- **Attachments** — Document/image uploads linked to any entity

**Important conventions:**

- All dates entered by the user are in **Jalali format** (`"1403/05/21"`). The API auto-converts and stores a parallel Gregorian date.
- All monetary values are in **Iranian Rials (IRR)**.
- All list endpoints return **paginated responses**.
- The API is versioned under `/api/v1/` to allow non-breaking future updates.

---

# 2. Key Concepts & Domain Glossary

| Term | Definition |
|------|-----------|
| **Truck Load** | A single trip from the mine to one of the grinding facilities. Each load has a receipt number, tonnage, driver, destination facility, and optional cost information. |
| **Bunker** | A transport record for moving ground ore from a grinding facility to the main processing factory. It includes the source facility, tonnage, and transport cost. |
| **Grinding Entry** | A ledger record for a grinding session at a specific facility. Tracks input tonnage (raw ore received), output tonnage (processed material), waste tonnage, and associated costs. |
| **Lab Batch** | A group of assay samples sent to the laboratory together on a specific date. Each batch can contain multiple individual lab results. |
| **Lab Result** | A single sample's gold assay reading, measured in **parts per million (ppm)**. The sample code is auto-parsed to extract the source facility, sample type, date, and sequence number. |
| **Payment Group** | A single bank payment transaction. It represents one deposit or transfer and may cover multiple supply chain records (e.g., paying for 3 truck loads and 2 bunker transports in one transaction). |
| **Payment Item** | One line within a Payment Group that links a specific payment amount (in Rials) to a specific entity using `entity_type` and `entity_id`. |
| **Attachment** | A file (PDF, image, scanned receipt) uploaded and linked to any entity (truck, bunker, grinding, lab batch, or payment group) for document management. |
| **RecordStatus** | The lifecycle status of a record. Values flow in order: `registered` → `costed` → `invoiced` → `paid`. |
| **GrindingFacility** | Enum identifying grinding sites: `robat_sefid` (رباط سفید), `shen_beton` (شن بتن), `kavian` (کاویان). |
| **EntityType** | Enum used by attachments and payments to identify which entity type they reference: `truck`, `bunker`, `lab_batch`, `grinding`, `payment_group`. |
| **SampleType** | Enum for lab sample categories: `K` (Cake/Solid), `L` (Solution/Liquid), `T` (Tailing), `CR` (Carbon), `RC` (Recovery Check). |

---

# 3. Data Models

## 3.1 Driver

### DriverCreate (Request Body)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `full_name` | string | ✅ | Driver's full name (Persian or Latin characters) |
| `iban` | string \| null | ❌ | Iranian IBAN for bank payments (e.g., `"IR290190000000102529858002"`) |
| `phone` | string \| null | ❌ | Phone number without country code (e.g., `"9155188319"`) |

### DriverUpdate (Request Body)

All fields are optional. Only provided fields will be updated.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `full_name` | string \| null | ❌ | Updated name |
| `iban` | string \| null | ❌ | Updated IBAN |
| `phone` | string \| null | ❌ | Updated phone |

### DriverResponse (Response)

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | integer | ✅ | Unique identifier |
| `full_name` | string | | Driver's full name |
| `iban` | string \| null | | IBAN |
| `phone` | string \| null | | Phone number |
| `created_at` | datetime | ✅ | Record creation timestamp (UTC) |
| `updated_at` | datetime | ✅ | Last update timestamp (UTC) |

---

## 3.2 Car

### CarCreate (Request Body)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plate_number` | string | ✅ | Vehicle plate number (must be unique). Example: `"14978"` |
| `current_driver_id` | integer \| null | ❌ | Foreign key to a driver record |

### CarUpdate (Request Body)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `plate_number` | string \| null | ❌ | Updated plate number |
| `current_driver_id` | integer \| null | ❌ | Updated driver assignment |

### CarResponse (Response)

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | integer | ✅ | Unique identifier |
| `plate_number` | string | | Vehicle plate number |
| `current_driver_id` | integer \| null | | Currently assigned driver ID |
| `current_driver` | DriverResponse \| null | ✅ | Nested driver object (populated on GET) |
| `created_at` | datetime | ✅ | Record creation timestamp |
| `updated_at` | datetime | ✅ | Last update timestamp |

---

## 3.3 Truck Load

### TruckLoadCreate (Request Body)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date_jalali` | string | ✅ | Trip date in Jalali format (e.g., `"1403/05/21"`) |
| `truck_plate_number` | string | ✅ | Plate number of the truck |
| `receipt_number` | integer | ✅ | Unique receipt/waybill number |
| `tonnage_kg` | integer | ✅ | Load weight in kilograms |
| `destination` | GrindingFacility | ✅ | Target grinding facility: `robat_sefid`, `shen_beton`, or `kavian` |
| `driver_name` | string | ✅ | Driver's name for this trip |
| `cost_per_ton_rials` | integer \| null | ❌ | Transport cost per ton in Rials |
| `total_cost_rials` | integer \| null | ❌ | Total transport cost in Rials |
| `notes` | string \| null | ❌ | Free-text notes |
| `status` | RecordStatus \| null | ❌ | Initial status (defaults to `registered`) |

### TruckLoadUpdate (Request Body)

All fields are optional. Only provided fields will be updated. When `cost_per_ton_rials` or `total_cost_rials` is set, the status auto-transitions to `costed`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date_jalali` | string \| null | ❌ | Updated date |
| `truck_plate_number` | string \| null | ❌ | Updated plate number |
| `receipt_number` | integer \| null | ❌ | Updated receipt number |
| `tonnage_kg` | integer \| null | ❌ | Updated tonnage |
| `destination` | GrindingFacility \| null | ❌ | Updated destination |
| `driver_name` | string \| null | ❌ | Updated driver name |
| `cost_per_ton_rials` | integer \| null | ❌ | Updated cost per ton |
| `total_cost_rials` | integer \| null | ❌ | Updated total cost |
| `notes` | string \| null | ❌ | Updated notes |

### TruckStatusPatch (Request Body for PATCH)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | RecordStatus | ✅ | New status: `registered`, `costed`, `invoiced`, or `paid` |

### TruckLoadResponse (Response)

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | integer | ✅ | Unique identifier |
| `date_jalali` | string | | Jalali date string |
| `date_gregorian` | date | ✅ | Auto-converted Gregorian date (ISO 8601) |
| `truck_plate_number` | string | | Plate number |
| `receipt_number` | integer | | Unique receipt number |
| `tonnage_kg` | integer | | Load weight in kg |
| `destination` | GrindingFacility | | Target facility |
| `driver_name` | string | | Driver's name |
| `cost_per_ton_rials` | integer \| null | | Cost per ton |
| `total_cost_rials` | integer \| null | | Total cost |
| `notes` | string \| null | | Notes |
| `status` | RecordStatus | ✅ | Current lifecycle status |
| `created_at` | datetime | ✅ | Creation timestamp |
| `updated_at` | datetime | ✅ | Last update timestamp |
| `attachments` | AttachmentResponse[] | ✅ | Attached files (populated on GET by ID) |

---

## 3.4 Bunker

### BunkerCreate (Request Body)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date_jalali` | string | ✅ | Transport date in Jalali format |
| `source_facility` | GrindingFacility | ✅ | Grinding facility this bunker originated from |
| `receipt_number` | integer | ✅ | Unique receipt number |
| `tonnage_kg` | integer | ✅ | Weight of ground ore in kg |
| `truck_plate_number` | string | ✅ | Plate number of the transport truck |
| `driver_name` | string | ✅ | Driver's name |
| `cost_per_ton_rials` | integer \| null | ❌ | Cost per ton in Rials |
| `total_cost_rials` | integer \| null | ❌ | Total transport cost |
| `notes` | string \| null | ❌ | Free-text notes |

### BunkerUpdate (Request Body)

All fields optional. Same fields as BunkerCreate but all nullable.

### BunkerResponse (Response)

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | integer | ✅ | Unique identifier |
| `date_jalali` | string | | Jalali date |
| `date_gregorian` | date | ✅ | Auto-converted Gregorian date |
| `source_facility` | GrindingFacility | | Origin facility |
| `receipt_number` | integer | | Unique receipt number |
| `tonnage_kg` | integer | | Weight in kg |
| `truck_plate_number` | string | | Plate number |
| `driver_name` | string | | Driver name |
| `cost_per_ton_rials` | integer \| null | | Cost per ton |
| `total_cost_rials` | integer \| null | | Total cost |
| `notes` | string \| null | | Notes |
| `status` | RecordStatus | ✅ | Lifecycle status |
| `created_at` | datetime | ✅ | Creation timestamp |
| `updated_at` | datetime | ✅ | Last update timestamp |
| `attachments` | AttachmentResponse[] | ✅ | Attached files |

---

## 3.5 Grinding

### GrindingCreate (Request Body)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date_jalali` | string | ✅ | Processing date in Jalali format |
| `facility` | GrindingFacility | ✅ | Which grinding facility: `robat_sefid`, `shen_beton`, or `kavian` |
| `input_tonnage_kg` | integer | ✅ | Raw ore input in kg |
| `output_tonnage_kg` | integer \| null | ❌ | Processed output in kg |
| `waste_tonnage_kg` | integer \| null | ❌ | Waste/tailings in kg |
| `grinding_cost_rials` | integer \| null | ❌ | Grinding processing cost |
| `transport_cost_rials` | integer \| null | ❌ | Transport cost to/from facility |
| `total_cost_rials` | integer \| null | ❌ | Total combined cost |
| `receipt_number` | integer \| null | ❌ | Receipt/invoice number (unique if provided) |
| `notes` | string \| null | ❌ | Free-text notes |

### GrindingUpdate (Request Body)

All fields optional. Same structure as GrindingCreate but all nullable.

### GrindingResponse (Response)

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | integer | ✅ | Unique identifier |
| `date_jalali` | string | | Jalali date |
| `date_gregorian` | date | ✅ | Auto-converted Gregorian date |
| `facility` | GrindingFacility | | Grinding facility |
| `input_tonnage_kg` | integer | | Raw ore input in kg |
| `output_tonnage_kg` | integer \| null | | Processed output in kg |
| `waste_tonnage_kg` | integer \| null | | Waste in kg |
| `grinding_cost_rials` | integer \| null | | Grinding cost |
| `transport_cost_rials` | integer \| null | | Transport cost |
| `total_cost_rials` | integer \| null | | Total cost |
| `receipt_number` | integer \| null | | Receipt number |
| `notes` | string \| null | | Notes |
| `status` | RecordStatus | ✅ | Lifecycle status |
| `created_at` | datetime | ✅ | Creation timestamp |
| `updated_at` | datetime | ✅ | Last update timestamp |
| `attachments` | AttachmentResponse[] | ✅ | Attached files |

---

## 3.6 Lab Batch

### LabBatchCreate (Request Body)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `issue_date_jalali` | string | ✅ | Date the batch was sent to the lab (Jalali format). Must be unique per batch. |
| `notes` | string \| null | ❌ | Notes about the batch |

### LabBatchUpdate (Request Body)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `analysis_count` | integer \| null | ❌ | Number of analyses performed |
| `total_cost_rials` | integer \| null | ❌ | Total lab analysis cost |
| `notes` | string \| null | ❌ | Updated notes |
| `status` | RecordStatus \| null | ❌ | Updated status |

### LabBatchResponse (Response)

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | integer | ✅ | Unique identifier |
| `issue_date_jalali` | string | | Jalali date |
| `issue_date_gregorian` | date | ✅ | Gregorian date |
| `analysis_count` | integer \| null | | Number of analyses |
| `total_cost_rials` | integer \| null | | Total cost |
| `status` | RecordStatus | ✅ | Lifecycle status |
| `notes` | string \| null | | Notes |
| `created_at` | datetime | ✅ | Creation timestamp |
| `updated_at` | datetime | ✅ | Last update timestamp |
| `results` | LabResultResponse[] | ✅ | Nested lab results (populated on GET by ID) |
| `results_count` | integer | ✅ | Number of results in this batch |
| `attachments` | AttachmentResponse[] | ✅ | Attached files |

---

## 3.7 Lab Result

### LabResultCreate (Request Body)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sample_code` | string | ✅ | Sample identifier code (e.g., `"A-1403/05/21-K-1"`). Auto-parsed to extract facility, date, type, and sequence. |
| `gold_ppm` | number \| string | ✅ | Gold concentration in parts per million. Accepts decimal numbers or numeric strings. |

**Sample Code Format:**

The system auto-parses sample codes using this convention:

- `A-1403/05/21-K-1` → Facility: `robat_sefid`, Date: `1403/05/21`, Type: `K` (Cake), Sequence: `1`
- `B-1403/05/21-L-3` → Facility: `shen_beton`, Date: `1403/05/21`, Type: `L` (Solution), Sequence: `3`
- `C-1403/05/21-CR-2` → Facility: `kavian`, Date: `1403/05/21`, Type: `CR` (Carbon), Sequence: `2`
- `RC-1403/05/21-1` → No facility, Type: `RC` (Recovery Check), Sequence: `1`

Facility prefix mapping: `A` = `robat_sefid`, `B` = `shen_beton`, `C` = `kavian`

Malformed codes are accepted but the parsed fields will be `null`.

### LabResultBulkCreate (Request Body)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `batch_id` | integer | ✅ | ID of the lab batch to add results to |
| `results` | LabResultCreate[] | ✅ | Array of result objects to create |

### LabResultUpdate (Request Body)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sample_code` | string \| null | ❌ | Updated sample code |
| `gold_ppm` | number \| string \| null | ❌ | Updated gold ppm |

### LabResultResponse (Response)

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | integer | ✅ | Unique identifier |
| `batch_id` | integer | ✅ | Parent batch ID |
| `sample_code` | string | | Original sample code string |
| `source_facility` | string \| null | ✅ | Auto-parsed facility name |
| `sample_date_jalali` | string \| null | ✅ | Auto-parsed Jalali date |
| `sample_date_gregorian` | date \| null | ✅ | Auto-parsed Gregorian date |
| `sample_type` | string \| null | ✅ | Auto-parsed sample type (`K`, `L`, `CR`, `T`, `RC`) |
| `sequence_number` | integer \| null | ✅ | Auto-parsed sequence number |
| `gold_ppm` | string | | Gold concentration as a decimal string (e.g., `"1.4500"`) |
| `created_at` | datetime | ✅ | Creation timestamp |
| `updated_at` | datetime | ✅ | Last update timestamp |

---

## 3.8 Payment Group

### PaymentGroupCreate (Request Body)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `payment_date_jalali` | string | ✅ | Payment date in Jalali format |
| `payment_time` | string \| null | ❌ | Time of payment (HH:MM:SS format) |
| `payer_name` | string | ✅ | Name of the payer |
| `bank_name` | string | ✅ | Name of the bank |
| `bank_account_number` | string \| null | ❌ | Bank account number |
| `total_amount_rials` | integer | ✅ | Total payment amount in Rials |
| `note` | string \| null | ❌ | Payment notes |
| `items` | PaymentItemCreate[] | ✅ | Array of payment line items |

### PaymentGroupUpdate (Request Body)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `payment_date_jalali` | string \| null | ❌ | Updated payment date |
| `payment_time` | string \| null | ❌ | Updated payment time |
| `payer_name` | string \| null | ❌ | Updated payer name |
| `bank_name` | string \| null | ❌ | Updated bank name |
| `bank_account_number` | string \| null | ❌ | Updated account number |
| `total_amount_rials` | integer \| null | ❌ | Updated total amount |
| `note` | string \| null | ❌ | Updated note |

### PaymentGroupResponse (Response)

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | integer | ✅ | Unique identifier |
| `payment_date_jalali` | string | | Jalali date |
| `payment_date_gregorian` | date | ✅ | Auto-converted Gregorian date |
| `payment_time` | string \| null | | Time of payment |
| `payer_name` | string | | Payer name |
| `bank_name` | string | | Bank name |
| `bank_account_number` | string \| null | | Account number |
| `total_amount_rials` | integer | | Total amount |
| `note` | string \| null | | Notes |
| `created_at` | datetime | ✅ | Creation timestamp |
| `items` | PaymentItemResponse[] | ✅ | Nested payment items |
| `items_count` | integer | ✅ | Number of items |

---

## 3.9 Payment Item

### PaymentItemCreate (Embedded in PaymentGroupCreate)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `entity_type` | EntityType | ✅ | Type of entity being paid for: `truck`, `bunker`, `grinding`, `lab_batch`, or `payment_group` |
| `entity_id` | integer | ✅ | ID of the entity being paid for |
| `amount_rials` | integer | ✅ | Payment amount for this entity in Rials |

### PaymentItemResponse (Response)

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | integer | ✅ | Unique identifier |
| `group_id` | integer | ✅ | Parent payment group ID |
| `entity_type` | string | | Entity type |
| `entity_id` | integer | | Entity ID |
| `amount_rials` | integer | | Payment amount |
| `created_at` | datetime | ✅ | Creation timestamp |

---

## 3.10 Attachment

### AttachmentResponse (Response)

| Field | Type | Read-Only | Description |
|-------|------|-----------|-------------|
| `id` | integer | ✅ | Unique identifier |
| `entity_type` | string | | Entity type this file belongs to |
| `entity_id` | integer | | Entity ID |
| `file_name` | string | ✅ | Original filename |
| `file_path` | string | ✅ | Server-side file path |
| `file_type` | string | ✅ | File extension (e.g., `"pdf"`, `"jpg"`) |
| `file_size_bytes` | integer \| null | ✅ | File size in bytes |
| `uploaded_at` | datetime | ✅ | Upload timestamp |

---

## 3.11 Paginated Response (Generic Wrapper)

All list endpoints return this structure:

| Field | Type | Description |
|-------|------|-------------|
| `items` | T[] | Array of records for the current page |
| `total` | integer | Total number of records matching the query |
| `page` | integer | Current page number |
| `size` | integer | Items per page |
| `pages` | integer | Total number of pages |

---

# 4. Endpoints Reference

---

## Drivers

### GET /api/v1/drivers/

**Summary:** List all registered truck drivers (paginated).

**Query Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `page` | integer | ❌ | 1 | Page number (min: 1) |
| `size` | integer | ❌ | 20 | Items per page (min: 1, max: 100) |

**Response:** `200 OK` — `PaginatedResponse<DriverResponse>`

```json
{
  "items": [
    {
      "id": 1,
      "full_name": "حسین طاووسی باغسیاه",
      "iban": "IR290190000000102529858002",
      "phone": "9155188319",
      "created_at": "2025-01-15T08:30:00Z",
      "updated_at": "2025-01-15T08:30:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

**Errors:** `422` — Invalid query parameters

---

### POST /api/v1/drivers/

**Summary:** Register a new truck driver.

**Request Body:** `DriverCreate`

```json
{
  "full_name": "احمد عرفانیان",
  "iban": "IR070120000000009101189676",
  "phone": "9151810135"
}
```

**Response:** `201 Created` — `DriverResponse`

```json
{
  "id": 7,
  "full_name": "احمد عرفانیان",
  "iban": "IR070120000000009101189676",
  "phone": "9151810135",
  "created_at": "2025-01-15T09:00:00Z",
  "updated_at": "2025-01-15T09:00:00Z"
}
```

**Errors:**
- `422` — Missing `full_name` or invalid data

---

### GET /api/v1/drivers/{driver_id}

**Summary:** Get a single driver by ID.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `driver_id` | integer | Driver's unique ID |

**Response:** `200 OK` — `DriverResponse`

**Errors:**
- `404` — Driver not found

---

### PUT /api/v1/drivers/{driver_id}

**Summary:** Update a driver's information.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `driver_id` | integer | Driver's unique ID |

**Request Body:** `DriverUpdate`

```json
{
  "phone": "9151234567"
}
```

**Response:** `200 OK` — `DriverResponse`

**Errors:**
- `404` — Driver not found
- `422` — Invalid data

---

### DELETE /api/v1/drivers/{driver_id}

**Summary:** Delete a driver. Fails if the driver is currently assigned to any car.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `driver_id` | integer | Driver's unique ID |

**Response:** `204 No Content`

**Errors:**
- `404` — Driver not found
- `409` — Driver is referenced by one or more cars (cannot delete)

---

## Cars

### GET /api/v1/cars/

**Summary:** List all registered vehicles (paginated), with optional driver filter.

**Query Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `driver_id` | integer | ❌ | — | Filter by assigned driver ID |
| `page` | integer | ❌ | 1 | Page number |
| `size` | integer | ❌ | 20 | Items per page |

**Response:** `200 OK` — `PaginatedResponse<CarResponse>`

```json
{
  "items": [
    {
      "id": 1,
      "plate_number": "14978",
      "current_driver_id": 1,
      "current_driver": {
        "id": 1,
        "full_name": "حسین طاووسی باغسیاه",
        "iban": "IR290190000000102529858002",
        "phone": "9155188319",
        "created_at": "2025-01-15T08:30:00Z",
        "updated_at": "2025-01-15T08:30:00Z"
      },
      "created_at": "2025-01-15T08:45:00Z",
      "updated_at": "2025-01-15T08:45:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

---

### POST /api/v1/cars/

**Summary:** Register a new vehicle.

**Request Body:** `CarCreate`

```json
{
  "plate_number": "81375",
  "current_driver_id": 2
}
```

**Response:** `201 Created` — `CarResponse`

**Errors:**
- `409` — Plate number already exists
- `422` — Invalid data

---

### GET /api/v1/cars/{car_id}

**Summary:** Get a single vehicle by ID, including its currently assigned driver.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `car_id` | integer | Car's unique ID |

**Response:** `200 OK` — `CarResponse`

**Errors:**
- `404` — Car not found

---

### PUT /api/v1/cars/{car_id}

**Summary:** Update a vehicle's plate number or driver assignment.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `car_id` | integer | Car's unique ID |

**Request Body:** `CarUpdate`

```json
{
  "current_driver_id": 5
}
```

**Response:** `200 OK` — `CarResponse`

**Errors:**
- `404` — Car not found
- `422` — Invalid data

---

### DELETE /api/v1/cars/{car_id}

**Summary:** Delete a vehicle record.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `car_id` | integer | Car's unique ID |

**Response:** `204 No Content`

**Errors:**
- `404` — Car not found

---

## Trucks

### GET /api/v1/trucks/

**Summary:** List all truck load records with optional filters for status, destination, and date range.

**Query Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `status` | RecordStatus | ❌ | — | Filter by lifecycle status |
| `destination` | GrindingFacility | ❌ | — | Filter by destination facility |
| `date_from` | string | ❌ | — | Start date (Jalali, e.g., `"1403/05/01"`) |
| `date_to` | string | ❌ | — | End date (Jalali, e.g., `"1403/05/31"`) |
| `page` | integer | ❌ | 1 | Page number |
| `size` | integer | ❌ | 20 | Items per page |

**Response:** `200 OK` — `PaginatedResponse<TruckLoadResponse>`

```json
{
  "items": [
    {
      "id": 1,
      "date_jalali": "1403/05/21",
      "date_gregorian": "2024-08-11",
      "truck_plate_number": "14978",
      "receipt_number": 5001,
      "tonnage_kg": 27000,
      "destination": "robat_sefid",
      "driver_name": "حسین طاووسی باغسیاه",
      "cost_per_ton_rials": 8700000,
      "total_cost_rials": 234900000,
      "notes": null,
      "status": "costed",
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-15T10:30:00Z",
      "attachments": []
    }
  ],
  "total": 4,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

---

### POST /api/v1/trucks/

**Summary:** Record a new truck load (a single mine → grinding facility trip).

**Request Body:** `TruckLoadCreate`

```json
{
  "date_jalali": "1403/05/21",
  "truck_plate_number": "14978",
  "receipt_number": 5001,
  "tonnage_kg": 27000,
  "destination": "robat_sefid",
  "driver_name": "حسین طاووسی باغسیاه",
  "cost_per_ton_rials": 8700000,
  "total_cost_rials": 234900000
}
```

**Response:** `201 Created` — `TruckLoadResponse`

**Errors:**
- `409` — Receipt number already exists
- `422` — Missing required fields or invalid Jalali date

---

### GET /api/v1/trucks/{truck_id}

**Summary:** Get a single truck load by ID, including its attached files.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `truck_id` | integer | Truck load's unique ID |

**Response:** `200 OK` — `TruckLoadResponse`

**Errors:**
- `404` — Truck load not found

---

### PUT /api/v1/trucks/{truck_id}

**Summary:** Update a truck load record. If cost fields are set and the current status is `registered`, the status auto-transitions to `costed`.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `truck_id` | integer | Truck load's unique ID |

**Request Body:** `TruckLoadUpdate`

```json
{
  "cost_per_ton_rials": 8700000,
  "total_cost_rials": 234900000
}
```

**Response:** `200 OK` — `TruckLoadResponse`

**Errors:**
- `404` — Truck load not found
- `422` — Invalid data

---

### DELETE /api/v1/trucks/{truck_id}

**Summary:** Delete a truck load. Only records with `registered` status can be deleted.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `truck_id` | integer | Truck load's unique ID |

**Response:** `204 No Content`

**Errors:**
- `404` — Not found
- `409` — Record is not in `registered` status (cannot delete costed/invoiced/paid records)

---

### PATCH /api/v1/trucks/{truck_id}/status

**Summary:** Manually change the lifecycle status of a truck load record.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `truck_id` | integer | Truck load's unique ID |

**Request Body:** `TruckStatusPatch`

```json
{
  "status": "invoiced"
}
```

**Response:** `200 OK` — `TruckLoadResponse`

**Errors:**
- `404` — Not found
- `422` — Invalid status value

---

## Bunkers

### GET /api/v1/bunkers/

**Summary:** List all bunker transport records with optional filters.

**Query Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `status` | RecordStatus | ❌ | — | Filter by status |
| `source_facility` | GrindingFacility | ❌ | — | Filter by source grinding facility |
| `date_from` | string | ❌ | — | Start date (Jalali) |
| `date_to` | string | ❌ | — | End date (Jalali) |
| `page` | integer | ❌ | 1 | Page number |
| `size` | integer | ❌ | 20 | Items per page |

**Response:** `200 OK` — `PaginatedResponse<BunkerResponse>`

```json
{
  "items": [
    {
      "id": 1,
      "date_jalali": "1403/05/22",
      "date_gregorian": "2024-08-12",
      "source_facility": "robat_sefid",
      "receipt_number": 8001,
      "tonnage_kg": 23560,
      "truck_plate_number": "14978",
      "driver_name": "محمد احمد آبادی",
      "cost_per_ton_rials": null,
      "total_cost_rials": null,
      "notes": null,
      "status": "registered",
      "created_at": "2025-01-15T11:00:00Z",
      "updated_at": "2025-01-15T11:00:00Z",
      "attachments": []
    }
  ],
  "total": 4,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

---

### POST /api/v1/bunkers/

**Summary:** Record a new bunker transport (grinding facility → factory).

**Request Body:** `BunkerCreate`

```json
{
  "date_jalali": "1403/05/22",
  "source_facility": "robat_sefid",
  "receipt_number": 8001,
  "tonnage_kg": 23560,
  "truck_plate_number": "14978",
  "driver_name": "محمد احمد آبادی"
}
```

**Response:** `201 Created` — `BunkerResponse`

**Errors:**
- `409` — Receipt number already exists
- `422` — Missing required fields or invalid data

---

### GET /api/v1/bunkers/{bunker_id}

**Summary:** Get a single bunker record by ID, including attachments.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `bunker_id` | integer | Bunker's unique ID |

**Response:** `200 OK` — `BunkerResponse`

**Errors:**
- `404` — Not found

---

### PUT /api/v1/bunkers/{bunker_id}

**Summary:** Update a bunker record. Cost fields trigger auto-transition to `costed`.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `bunker_id` | integer | Bunker's unique ID |

**Request Body:** `BunkerUpdate`

```json
{
  "cost_per_ton_rials": 5200000,
  "total_cost_rials": 122512000
}
```

**Response:** `200 OK` — `BunkerResponse`

**Errors:**
- `404` — Not found
- `422` — Invalid data

---

### DELETE /api/v1/bunkers/{bunker_id}

**Summary:** Delete a bunker record (only `registered` status).

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `bunker_id` | integer | Bunker's unique ID |

**Response:** `204 No Content`

**Errors:**
- `404` — Not found
- `409` — Record not in `registered` status

---

## Grinding

### GET /api/v1/grinding/

**Summary:** List all grinding ledger entries with optional filters.

**Query Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `status` | RecordStatus | ❌ | — | Filter by status |
| `facility` | GrindingFacility | ❌ | — | Filter by grinding facility |
| `date_from` | string | ❌ | — | Start date (Jalali) |
| `date_to` | string | ❌ | — | End date (Jalali) |
| `page` | integer | ❌ | 1 | Page number |
| `size` | integer | ❌ | 20 | Items per page |

**Response:** `200 OK` — `PaginatedResponse<GrindingResponse>`

```json
{
  "items": [
    {
      "id": 1,
      "date_jalali": "1403/05/20",
      "date_gregorian": "2024-08-10",
      "facility": "robat_sefid",
      "input_tonnage_kg": 54000,
      "output_tonnage_kg": 51200,
      "waste_tonnage_kg": 2800,
      "grinding_cost_rials": 162000000,
      "transport_cost_rials": null,
      "total_cost_rials": 162000000,
      "receipt_number": 7001,
      "notes": "Standard grinding batch",
      "status": "costed",
      "created_at": "2025-01-15T07:00:00Z",
      "updated_at": "2025-01-15T07:30:00Z",
      "attachments": []
    }
  ],
  "total": 5,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

---

### POST /api/v1/grinding/

**Summary:** Record a new grinding session at a facility.

**Request Body:** `GrindingCreate`

```json
{
  "date_jalali": "1403/05/20",
  "facility": "robat_sefid",
  "input_tonnage_kg": 54000,
  "output_tonnage_kg": 51200,
  "waste_tonnage_kg": 2800,
  "grinding_cost_rials": 162000000,
  "receipt_number": 7001,
  "notes": "Standard grinding batch"
}
```

**Response:** `201 Created` — `GrindingResponse`

**Errors:**
- `409` — Receipt number already exists
- `422` — Missing required fields

---

### GET /api/v1/grinding/{entry_id}

**Summary:** Get a single grinding entry by ID, including attachments.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `entry_id` | integer | Grinding entry's unique ID |

**Response:** `200 OK` — `GrindingResponse`

**Errors:**
- `404` — Not found

---

### PUT /api/v1/grinding/{entry_id}

**Summary:** Update a grinding entry. Cost fields trigger auto-transition to `costed`.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `entry_id` | integer | Grinding entry's unique ID |

**Request Body:** `GrindingUpdate`

```json
{
  "total_cost_rials": 175000000,
  "notes": "Updated cost after transport adjustment"
}
```

**Response:** `200 OK` — `GrindingResponse`

**Errors:**
- `404` — Not found
- `422` — Invalid data

---

### DELETE /api/v1/grinding/{entry_id}

**Summary:** Delete a grinding entry (only `registered` status).

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `entry_id` | integer | Grinding entry's unique ID |

**Response:** `204 No Content`

**Errors:**
- `404` — Not found
- `409` — Record not in `registered` status

---

## Lab — Batches

### GET /api/v1/lab/batches/

**Summary:** List all lab analysis batches with optional filters.

**Query Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `status` | RecordStatus | ❌ | — | Filter by status |
| `date_from` | string | ❌ | — | Start date (Jalali) |
| `date_to` | string | ❌ | — | End date (Jalali) |
| `page` | integer | ❌ | 1 | Page number |
| `size` | integer | ❌ | 20 | Items per page |

**Response:** `200 OK` — `PaginatedResponse<LabBatchResponse>`

```json
{
  "items": [
    {
      "id": 1,
      "issue_date_jalali": "1403/05/21",
      "issue_date_gregorian": "2024-08-11",
      "analysis_count": null,
      "total_cost_rials": null,
      "status": "registered",
      "notes": null,
      "created_at": "2025-01-15T12:00:00Z",
      "updated_at": "2025-01-15T12:00:00Z",
      "results": [],
      "results_count": 0,
      "attachments": []
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

---

### POST /api/v1/lab/batches/

**Summary:** Create a new lab analysis batch for a given date.

**Request Body:** `LabBatchCreate`

```json
{
  "issue_date_jalali": "1403/05/21",
  "notes": "Samples from Robat Sefid facility"
}
```

**Response:** `201 Created` — `LabBatchResponse`

**Errors:**
- `409` — A batch already exists for this Jalali date
- `422` — Invalid date format

---

### GET /api/v1/lab/batches/{batch_id}

**Summary:** Get a batch with all its lab results and attachments.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `batch_id` | integer | Batch's unique ID |

**Response:** `200 OK` — `LabBatchResponse` (with nested `results` and `attachments`)

```json
{
  "id": 1,
  "issue_date_jalali": "1403/05/21",
  "issue_date_gregorian": "2024-08-11",
  "analysis_count": null,
  "total_cost_rials": null,
  "status": "registered",
  "notes": null,
  "created_at": "2025-01-15T12:00:00Z",
  "updated_at": "2025-01-15T12:00:00Z",
  "results": [
    {
      "id": 1,
      "batch_id": 1,
      "sample_code": "A-1403/05/21-K-1",
      "source_facility": "robat_sefid",
      "sample_date_jalali": "1403/05/21",
      "sample_date_gregorian": "2024-08-11",
      "sample_type": "K",
      "sequence_number": 1,
      "gold_ppm": "1.4500",
      "created_at": "2025-01-15T12:10:00Z",
      "updated_at": "2025-01-15T12:10:00Z"
    }
  ],
  "results_count": 1,
  "attachments": []
}
```

**Errors:**
- `404` — Batch not found

---

### PUT /api/v1/lab/batches/{batch_id}

**Summary:** Update batch metadata (analysis count, cost, status, notes).

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `batch_id` | integer | Batch's unique ID |

**Request Body:** `LabBatchUpdate`

```json
{
  "analysis_count": 12,
  "total_cost_rials": 36000000,
  "status": "invoiced"
}
```

**Response:** `200 OK` — `LabBatchResponse`

**Errors:**
- `404` — Not found
- `422` — Invalid data

---

### DELETE /api/v1/lab/batches/{batch_id}

**Summary:** Delete a lab batch. Fails if the batch contains any results.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `batch_id` | integer | Batch's unique ID |

**Response:** `204 No Content`

**Errors:**
- `404` — Not found
- `409` — Batch has results (delete results first)

---

## Lab — Results

### GET /api/v1/lab/results/

**Summary:** List all lab results with optional filters.

**Query Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `batch_id` | integer | ❌ | — | Filter by parent batch ID |
| `sample_type` | SampleType | ❌ | — | Filter by sample type: `K`, `L`, `CR`, `T`, `RC` |
| `source_facility` | GrindingFacility | ❌ | — | Filter by source facility |
| `page` | integer | ❌ | 1 | Page number |
| `size` | integer | ❌ | 20 | Items per page |

**Response:** `200 OK` — `PaginatedResponse<LabResultResponse>`

```json
{
  "items": [
    {
      "id": 1,
      "batch_id": 1,
      "sample_code": "A-1403/05/21-K-1",
      "source_facility": "robat_sefid",
      "sample_date_jalali": "1403/05/21",
      "sample_date_gregorian": "2024-08-11",
      "sample_type": "K",
      "sequence_number": 1,
      "gold_ppm": "1.4500",
      "created_at": "2025-01-15T12:10:00Z",
      "updated_at": "2025-01-15T12:10:00Z"
    },
    {
      "id": 2,
      "batch_id": 1,
      "sample_code": "A-1403/05/21-L-1",
      "source_facility": "robat_sefid",
      "sample_date_jalali": "1403/05/21",
      "sample_date_gregorian": "2024-08-11",
      "sample_type": "L",
      "sequence_number": 1,
      "gold_ppm": "0.2800",
      "created_at": "2025-01-15T12:11:00Z",
      "updated_at": "2025-01-15T12:11:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

---

### POST /api/v1/lab/results/?batch_id={batch_id}

**Summary:** Add a single lab result to a batch. The sample code is auto-parsed.

**Query Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `batch_id` | integer | ✅ | ID of the batch to add this result to |

**Request Body:** `LabResultCreate`

```json
{
  "sample_code": "A-1403/05/21-K-1",
  "gold_ppm": 1.45
}
```

**Response:** `201 Created` — `LabResultResponse`

**Errors:**
- `404` — Batch not found
- `422` — Invalid data

---

### POST /api/v1/lab/results/bulk

**Summary:** Add multiple lab results to a batch in one request.

**Request Body:** `LabResultBulkCreate`

```json
{
  "batch_id": 1,
  "results": [
    { "sample_code": "A-1403/05/21-K-1", "gold_ppm": 1.45 },
    { "sample_code": "A-1403/05/21-L-1", "gold_ppm": 0.28 },
    { "sample_code": "A-1403/05/21-CR-1", "gold_ppm": 485.0 },
    { "sample_code": "RC-1403/05/21-1", "gold_ppm": 0.02 }
  ]
}
```

**Response:** `201 Created` — `LabResultResponse[]`

```json
[
  {
    "id": 1,
    "batch_id": 1,
    "sample_code": "A-1403/05/21-K-1",
    "source_facility": "robat_sefid",
    "sample_date_jalali": "1403/05/21",
    "sample_date_gregorian": "2024-08-11",
    "sample_type": "K",
    "sequence_number": 1,
    "gold_ppm": "1.4500",
    "created_at": "2025-01-15T12:10:00Z",
    "updated_at": "2025-01-15T12:10:00Z"
  },
  {
    "id": 2,
    "batch_id": 1,
    "sample_code": "A-1403/05/21-L-1",
    "source_facility": "robat_sefid",
    "sample_date_jalali": "1403/05/21",
    "sample_date_gregorian": "2024-08-11",
    "sample_type": "L",
    "sequence_number": 1,
    "gold_ppm": "0.2800",
    "created_at": "2025-01-15T12:11:00Z",
    "updated_at": "2025-01-15T12:11:00Z"
  },
  {
    "id": 3,
    "batch_id": 1,
    "sample_code": "A-1403/05/21-CR-1",
    "source_facility": "robat_sefid",
    "sample_date_jalali": "1403/05/21",
    "sample_date_gregorian": "2024-08-11",
    "sample_type": "CR",
    "sequence_number": 1,
    "gold_ppm": "485.0000",
    "created_at": "2025-01-15T12:12:00Z",
    "updated_at": "2025-01-15T12:12:00Z"
  },
  {
    "id": 4,
    "batch_id": 1,
    "sample_code": "RC-1403/05/21-1",
    "source_facility": null,
    "sample_date_jalali": "1403/05/21",
    "sample_date_gregorian": "2024-08-11",
    "sample_type": "RC",
    "sequence_number": 1,
    "gold_ppm": "0.0200",
    "created_at": "2025-01-15T12:13:00Z",
    "updated_at": "2025-01-15T12:13:00Z"
  }
]
```

**Errors:**
- `404` — Batch not found
- `422` — Invalid data in one or more results

---

### GET /api/v1/lab/results/{result_id}

**Summary:** Get a single lab result by ID.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `result_id` | integer | Result's unique ID |

**Response:** `200 OK` — `LabResultResponse`

**Errors:**
- `404` — Not found

---

### PUT /api/v1/lab/results/{result_id}

**Summary:** Update a lab result's sample code or gold ppm value.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `result_id` | integer | Result's unique ID |

**Request Body:** `LabResultUpdate`

```json
{
  "gold_ppm": 1.52
}
```

**Response:** `200 OK` — `LabResultResponse`

**Errors:**
- `404` — Not found
- `422` — Invalid data

---

### DELETE /api/v1/lab/results/{result_id}

**Summary:** Delete a single lab result.

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `result_id` | integer | Result's unique ID |

**Response:** `204 No Content`

**Errors:**
- `404` — Not found

---

## Payments

### GET /api/v1/payments/groups/

**Summary:** List all payment groups (bank transactions) with optional filters.

**Query Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `date_from` | string | ❌ | — | Start date (Jalali) |
| `date_to` | string | ❌ | — | End date (Jalali) |
| `payer_name` | string | ❌ | — | Filter by payer name (substring match) |
| `bank_name` | string | ❌ | — | Filter by bank name (substring match) |
| `page` | integer | ❌ | 1 | Page number |
| `size` | integer | ❌ | 20 | Items per page |

**Response:** `200 OK` — `PaginatedResponse<PaymentGroupResponse>`

```json
{
  "items": [
    {
      "id": 1,
      "payment_date_jalali": "1403/06/15",
      "payment_date_gregorian": "2024-09-05",
      "payment_time": "14:30:00",
      "payer_name": "شرکت زرین معدن",
      "bank_name": "بانک ملت",
      "bank_account_number": "6104337812345678",
      "total_amount_rials": 500000000,
      "note": "پرداخت حمل و نقل شهریور",
      "created_at": "2025-01-16T08:00:00Z",
      "items": [
        {
          "id": 1,
          "group_id": 1,
          "entity_type": "truck",
          "entity_id": 1,
          "amount_rials": 234900000,
          "created_at": "2025-01-16T08:00:00Z"
        },
        {
          "id": 2,
          "group_id": 1,
          "entity_type": "bunker",
          "entity_id": 1,
          "amount_rials": 265100000,
          "created_at": "2025-01-16T08:00:00Z"
        }
      ],
      "items_count": 2
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

---

### POST /api/v1/payments/groups/

**Summary:** Create a new payment group (bank transaction) with one or more payment items. Each referenced entity must exist and be in `costed` or `invoiced` status. After payment, entities are transitioned to `paid`.

**Request Body:** `PaymentGroupCreate`

```json
{
  "payment_date_jalali": "1403/06/15",
  "payment_time": "14:30:00",
  "payer_name": "شرکت زرین معدن",
  "bank_name": "بانک ملت",
  "bank_account_number": "6104337812345678",
  "total_amount_rials": 500000000,
  "note": "پرداخت حمل و نقل شهریور",
  "items": [
    { "entity_type": "truck", "entity_id": 1, "amount_rials": 234900000 },
    { "entity_type": "bunker", "entity_id": 1, "amount_rials": 265100000 }
  ]
}
```

**Response:** `201 Created` — `PaymentGroupResponse`

**Errors:**
- `404` — One of the referenced entities does not exist
- `400` — Entity is in `registered` status (