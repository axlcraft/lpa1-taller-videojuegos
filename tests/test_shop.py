class TestShop:
    def test_creation(self, shop):
        assert shop is not None
        assert hasattr(shop, 'items')
        assert len(shop.items) >= 1
        assert hasattr(shop, 'continue_button')

    def test_shop_items_have_properties(self, shop):
        for item in shop.items:
            assert hasattr(item, 'name')
            assert hasattr(item, 'get_current_price')
            assert hasattr(item, 'description')
            assert item.get_current_price() > 0

    def test_can_purchase(self, shop):
        for item in shop.items:
            if item.purchase_count < item.max_purchases:
                assert item.can_purchase() is True
            else:
                assert item.can_purchase() is False

    def test_purchase_item(self, shop):
        for item in shop.items:
            if item.can_purchase():
                price_before = item.get_current_price()
                count_before = item.purchase_count
                result = item.purchase_item()
                assert result is True
                assert item.purchase_count == count_before + 1
                if item.purchase_count < item.max_purchases:
                    assert item.get_current_price() > price_before
                break

    def test_max_purchases_limit(self, shop):
        for item in shop.items:
            while item.can_purchase():
                item.purchase_item()
            assert item.can_purchase() is False
            break

    def test_max_purchases_default(self, shop):
        for item in shop.items:
            assert item.max_purchases > 0
            break

    def test_item_types(self, shop):
        types = {item.item_type for item in shop.items}
        assert "health" in types

    def test_reset_purchases(self, shop):
        for item in shop.items:
            if item.item_type == "health":
                item.purchase_item()
                assert item.purchase_count > 0
                shop.reset_purchases()
                assert item.purchase_count == 0
                assert item.purchased is False
                assert item.price == item.base_price
                break
