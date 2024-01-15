# Makerspace CRM RESTful API Documentation

## Overview

This RESTful API provides comprehensive management capabilities for a Makerspace community. It's designed as a Customer Relationship Management (CRM) tool, facilitating the organization of members, equipment, access control, and various administrative tasks.

### Features

1. **Member Management**
   - Manage member profiles including personal information, emergency contacts, and billing details.
   - Track member activity, membership types, and billing cadence.
   - Securely handle member credentials and preferences.

2. **Access Control**
   - Control and monitor access to different areas using door profiles and keycards.
   - Define time-based access permissions for various member categories.
   - Log access events for security and auditing purposes.

3. **Equipment Management**
   - Catalogue equipment with details like serial number, model, and procurement data.
   - Track equipment status (operational, out of order) and maintenance history.
   - Manage documentation related to donations and equipment loans.

4. **Training & Compliance**
   - Keep records of members trained on specific equipment.
   - Manage contracts and waivers signed by members.
   - Ensure compliance with training requirements for equipment usage.

5. **Billing & Financials**
   - Log and track billing events and member payment statuses.
   - Manage different billing plans and cadences.
   - Integrate with external billing systems like QuickBooks.

6. **Reporting & Analytics**
   - Generate reports on access logs, equipment usage, and member activities.
   - Analyze data for insights into Makerspace operations and member engagement.

7. **Customizable Forms and Documents**
   - Create and manage various forms for members to fill out.
   - Store and retrieve important documents and images like contracts and equipment photos.

8. **Role-Based Access Control (RBAC)**
   - Define roles with specific permissions for different levels of access within the CRM.
   - Assign roles to members for administrative tasks and access control.

## API Endpoints Documentation for Makerspace CRM

Below are detailed API endpoints for managing the Makerspace CRM, with descriptions of their functionalities:

### Member Management

#### Get Member
- `GET /person/{person_id}`
  - Retrieves information about a specific member by their ID.
  - Returns member details such as name, billing reference, and membership status.

#### Delete Member (Soft Delete)
- `DELETE /person/{person_id}`
  - Soft deletes a member by setting a flag in the database, effectively hiding them from normal queries.
  - Returns a confirmation message upon successful soft deletion.

#### Update Member
- `PUT /person/{person_id}`
  - Updates member information such as name, billing reference, and membership status.
  - Requires `first`, `last`, `billing_ref`, `is_member_active`, and `is_member_paid` as input parameters.

#### Patch Member
- `PATCH /person/{person_id}`
  - Allows for restoring a soft-deleted member or performing a hard delete.
  - Requires `restore_softdelete` or `hard_delete` as input parameters.

#### Create Member
- `POST /person`
  - Creates a new member record.
  - Requires `first`, `last`, `billing_ref`, `is_member_active`, and `is_member_paid` as input parameters.

### Membership Type Management

#### Get Membership Type
- `GET /membershipTypeMap/{type_id}`
  - Retrieves information about a specific membership type by its ID.
  - Returns membership type details such as name and description.

#### Delete Membership Type
- `DELETE /membershipTypeMap/{type_id}`
  - Deletes a specific membership type by its ID.
  - Returns a confirmation message upon successful deletion.

#### Update Membership Type
- `PUT /membershipTypeMap/{type_id}`
  - Updates membership type information such as name and description.
  - Requires `name` and `description` as input parameters.

### Equipment Management

#### Create Person-Equipment Association
- `POST /personAllowedEquipment`
  - Creates an association between a person and equipment, indicating what equipment a person is allowed to use.
  - Requires `equipment_id` and `person_id` as input parameters.

### Contract Management

#### Get Contract Type
- `GET /contractTypeMap/{type_id}`
  - Retrieves information about a specific contract type by its ID.
  - Returns contract type details such as name and description.

#### Create Contract Type
- `POST /contractTypeMap`
  - Creates a new contract type.
  - Requires `name` and `description` as input parameters.

#### Delete Contract Type
- `DELETE /contractTypeMap/{type_id}`
  - Deletes a specific contract type by its ID.
  - Returns a confirmation message upon successful deletion.

#### Update Contract Type
- `PUT /contractTypeMap/{type_id}`
  - Updates contract type information such as name and description.
  - Requires `name` and `description` as input parameters.

### Location & Zone Management

#### Get All Locations
- `GET /allLocations`
  - Retrieves a list of all locations.

#### Get All Zones
- `GET /allZones`
  - Retrieves a list of all zones, including associated location information.

### Miscellaneous

#### Get Person's Memberships
- `GET /personMembership/{person_id}`
  - Retrieves all membership types associated with a specific person.

#### Get Person's Billing Cadences
- `GET /personBillingCadence/{person_id}`
  - Retrieves all billing cadences associated with a specific person.