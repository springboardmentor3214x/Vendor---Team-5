"""Module 8 API-schema regression checks for project and manager fields."""

from datetime import date, datetime

from app.schemas.procurement import ProcurementRequestCreate, PurchaseOrderCreate


def test_module8_project_and_assigned_manager_aliases_are_accepted() -> None:
    request = ProcurementRequestCreate.model_validate(
        {
            "requestTitle": "Project material order",
            "departmentName": "Operations",
            "projectName": "Alpha Expansion",
            "itemDescription": "Materials for the expansion project",
            "itemProductName": "Steel sheets",
            "productCategory": "Materials",
            "quantityRequired": 2,
            "estimatedBudget": 5000,
            "requiredDeliveryDate": date.today().isoformat(),
            "businessJustification": "Required for the approved project scope",
        }
    )
    purchase_order = PurchaseOrderCreate.model_validate(
        {
            "procurementRequestId": 1,
            "quantityOrdered": 2,
            "unitPrice": 2500,
            "expectedDeliveryDate": datetime(2026, 9, 1, 10, 0).isoformat(),
            "assignedProcurementManagerId": 7,
            "projectName": "Alpha Expansion",
        }
    )

    assert request.project_name == "Alpha Expansion"
    assert purchase_order.assigned_procurement_manager_id == 7
    assert purchase_order.project_name == "Alpha Expansion"
