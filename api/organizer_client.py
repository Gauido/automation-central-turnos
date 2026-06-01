from typing import Any

from api.base_client import BaseClient


class OrganizerClient(BaseClient):
    def list_tournaments(self):
        return self.get("/api/organizer/tournaments")

    def create_tournament(self, payload: dict[str, Any]):
        return self.post("/api/organizer/tournaments", json=payload)

    def get_tournament(self, tournament_id: int | str):
        return self.get(f"/api/organizer/tournaments/{tournament_id}")

    def update_tournament(self, tournament_id: int | str, payload: dict[str, Any]):
        return self.request("PUT", f"/api/organizer/tournaments/{tournament_id}", json=payload)

    def delete_tournament(self, tournament_id: int | str):
        return self.request("DELETE", f"/api/organizer/tournaments/{tournament_id}")

    def list_categories(self, tournament_id: int | str):
        return self.get(f"/api/organizer/tournaments/{tournament_id}/categories")

    def create_category(self, tournament_id: int | str, payload: dict[str, Any]):
        return self.post(f"/api/organizer/tournaments/{tournament_id}/categories", json=payload)

    def update_category(self, category_id: int | str, payload: dict[str, Any]):
        return self.request("PUT", f"/api/organizer/categories/{category_id}", json=payload)

    def delete_category(self, category_id: int | str):
        return self.request("DELETE", f"/api/organizer/categories/{category_id}")

    def create_pair(self, category_id: int | str, payload: dict[str, Any]):
        return self.post(f"/api/organizer/categories/{category_id}/pairs", json=payload)

    def update_pair(self, pair_id: int | str, payload: dict[str, Any]):
        return self.request("PUT", f"/api/organizer/pairs/{pair_id}", json=payload)

    def delete_pair(self, pair_id: int | str):
        return self.request("DELETE", f"/api/organizer/pairs/{pair_id}")

    def random_assign_zones(self, category_id: int | str, payload: dict[str, Any]):
        return self.post(f"/api/organizer/categories/{category_id}/zones/random-assign", json=payload)

    def create_zones(self, category_id: int | str, payload: dict[str, Any]):
        return self.post(f"/api/organizer/categories/{category_id}/zones", json=payload)

    def list_zones(self, category_id: int | str):
        return self.get(f"/api/organizer/categories/{category_id}/zones")

    def generate_matches(self, category_id: int | str):
        return self.post(f"/api/organizer/categories/{category_id}/zones/generate-matches", json={})

    def list_zone_matches(self, zone_id: int | str):
        return self.get(f"/api/organizer/zones/{zone_id}/matches")

    def list_pairs(self, category_id: int | str):
        return self.get(f"/api/organizer/categories/{category_id}/pairs")

    def add_pair_payment(self, pair_id: int | str, payload: dict[str, Any]):
        return self.post(f"/api/organizer/pairs/{pair_id}/payments", json=payload)

    def set_match_result(self, match_id: int | str, payload: dict[str, Any]):
        return self.post(f"/api/organizer/matches/{match_id}/result", json=payload)

    def close_zone(self, zone_id: int | str):
        return self.post(f"/api/organizer/zones/{zone_id}/close", json={})

    def reopen_zone(self, zone_id: int | str):
        return self.post(f"/api/organizer/zones/{zone_id}/reopen", json={})

    def remove_pair_from_zone(self, zone_id: int | str, pair_id: int | str):
        return self.request("DELETE", f"/api/organizer/zones/{zone_id}/pairs/{pair_id}")

    def build_bracket(self, category_id: int | str):
        return self.post(f"/api/organizer/categories/{category_id}/build-bracket", json={})

    def podium(self, tournament_id: int | str):
        return self.get(f"/api/organizer/tournaments/{tournament_id}/podium")

    def report(self, tournament_id: int | str):
        return self.get(f"/api/organizer/tournaments/{tournament_id}/report")
