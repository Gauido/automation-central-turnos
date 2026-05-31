from api.base_client import BaseClient


class TenantModulesClient(BaseClient):
    def list_tenants(self):
        return self.get("/api/admin/tenant-modules/tenants")

    def tenant_modules(self, tenant_id: int | str):
        return self.get(f"/api/admin/tenant-modules/{tenant_id}")

    def set_module(self, tenant_id: int | str, module_key: str, enabled: bool):
        return self.request("PUT", f"/api/admin/tenant-modules/{tenant_id}/{module_key}", json={"enabled": enabled})

    def my_modules(self):
        return self.get("/api/Tenants/me/modules")
