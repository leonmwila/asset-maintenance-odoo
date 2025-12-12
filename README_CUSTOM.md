# Asset Maintenance MIS - Custom Modules

Custom Odoo 19.0 modules for Asset Maintenance Management Information System.

## Modules

### 1. company_extension
Enhanced multi-company functionality with Zambian government integration.

**Features:**
- **Multi-Company Support**: Province, District, and location management
- **GRZ Number Auto-generation**: Automatic generation based on company type
- **Serial Range Management**: Track and validate GRZ serial number ranges
- **Programs & Projects**: OE Program and Project management with multi-company support
- **Cross-Company Repairs**: Allow technicians to repair equipment from any company
- **Parts Approval Workflow**: Added approval stage for repair parts before starting repairs
- **Zambian Flag Theme**: Green and orange color scheme for the interface

**Models:**
- `res.company` - Extended with Province, District, Company Type
- `res.location` - Province model
- `res.district` - District model  
- `res.serial.range` - GRZ serial number range tracking
- `stock.lot` - Auto-generate GRZ numbers
- `repair.order` - Cross-company lot selection and parts approval
- `oe.program` - Program management
- `oe.project` - Project management
- `product.category` - GRZ category tracking

**Workflow:**
1. New/Draft - Create repair order
2. Confirmed - Confirm the repair and add parts
3. Parts Approved - Approve selected parts (new stage)
4. Under Repair - Start repair work
5. Repaired - Complete repair

### 2. equipment_serial_link
Links maintenance equipment with serial numbers (lots).

**Features:**
- Validates GRZ serial number ranges during lot creation
- Ensures serial numbers are within assigned ranges for GRZ companies

**Models:**
- `stock.lot` - GRZ range validation
- `maintenance.equipment` - Serial number linking

## Installation

1. Clone this repository
2. Copy `custom_addons` to your Odoo addons path
3. Update Odoo addons list
4. Install the modules from Apps menu

## Configuration

### GRZ Number Setup
1. Go to Settings > Companies
2. Set Company Type to "Government (GRZ)"
3. Configure serial number ranges in the Serial Ranges tab
4. GRZ numbers will auto-generate when creating lots/serials

### Theme
The Zambian flag green (#198A00) and orange (#DE6B2D) theme is automatically applied system-wide.

## Technical Details

**Dependencies:**
- base
- stock
- product
- repair

**Odoo Version:** 19.0

**License:** LGPL-3

## Author
Leon Mwila
