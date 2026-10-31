import pytest

import mini_store.shop as shop_module
from mini_store.context import Daily, GameContext
from mini_store.player import Player
from mini_store.shop import Shop, ShopAction, ShopItem


@pytest.fixture
def shop(ctx: GameContext, monkeypatch: pytest.MonkeyPatch) -> Shop:
    monkeypatch.setattr(shop_module, 'cls', lambda: None)
    return Shop(ctx)


class TestCatalog:
    def test_default_prices(self, shop: Shop) -> None:
        prices = {item.id: item.price for item in shop.catalog}

        assert prices == {
            1: 200,
            2: 200,
            3: 300,
            4: 300,
            5: 500,
            6: 400,
            7: 700,
            8: 1200,
            9: 2500,
        }

    def test_maxed_items_have_no_price(self, shop: Shop) -> None:
        shop.player.balance_multiplier = 5
        shop.player.xp_multiplier = 5
        shop.player.mining_lvl = 10

        catalog = shop._build_catalog()

        assert catalog[0].price is None
        assert catalog[1].price is None
        assert catalog[3].price is None

    def test_names_include_current_multiplier(self, shop: Shop) -> None:
        shop.player.balance_multiplier = 3
        shop.player.xp_multiplier = 4

        catalog = shop._build_catalog()

        assert catalog[0].name == 'Множитель монет 3x'
        assert catalog[1].name == 'Множитель опыта 4x'

    def test_catalog_is_indexed_by_id(self, shop: Shop) -> None:
        assert shop.catalog_by_id[9].name == 'Секретный кейс'


class TestPriceLabels:
    def test_regular_price(self, shop: Shop) -> None:
        assert shop._price_label(shop.catalog_by_id[3]) == '300 монет'

    def test_max_price(self, shop: Shop) -> None:
        shop.player.balance_multiplier = 5
        item = shop._build_catalog()[0]

        assert 'MAX' in shop._price_label(item)

    def test_discount_label(self, shop: Shop) -> None:
        shop.ctx.daily.discount_item_id = 3
        label = shop._price_label(shop.catalog_by_id[3])

        assert '300' in label
        assert '240' in label
        assert 'СКИДКА' in label

    def test_final_price_without_discount(self, shop: Shop) -> None:
        assert shop._final_price(shop.catalog_by_id[3]) == 300

    def test_final_price_with_discount(self, shop: Shop) -> None:
        shop.ctx.daily.discount_item_id = 5

        assert shop._final_price(shop.catalog_by_id[5]) == 400


class TestDiscount:
    def test_no_discount(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop.ctx.daily.discount_item_id = 3
        monkeypatch.setattr(shop_module.random, 'random', lambda: 0.5)

        shop._roll_discount()

        assert shop.ctx.daily.discount_item_id is None

    def test_discount_is_applied(
        self,
        shop: Shop,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr(shop_module.random, 'random', lambda: 0.1)
        monkeypatch.setattr(
            shop_module.random, 'choice', lambda _items: shop.catalog_by_id[9]
        )

        shop._roll_discount()

        assert shop.ctx.daily.discount_item_id == 9
        assert 'Секретный кейс' in capsys.readouterr().out


class TestBuy:
    def test_buy_unique_item(self, shop: Shop) -> None:
        shop.player.balance = 1000

        shop._buy(shop.catalog_by_id[3])

        assert shop.player.lucky_amulet is True
        assert shop.player.balance == 700

    def test_cannot_buy_unique_item_twice(self, shop: Shop) -> None:
        shop.player.balance = 1000
        shop.player.lucky_amulet = True

        shop._buy(shop.catalog_by_id[3])

        assert shop.player.balance == 1000

    def test_not_enough_money(self, shop: Shop) -> None:
        shop.player.balance = 100

        shop._buy(shop.catalog_by_id[3])

        assert shop.player.lucky_amulet is False
        assert shop.player.balance == 100

    def test_buy_multiplier_with_confirmation(
        self, shop: Shop, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        shop.player.balance = 1000
        monkeypatch.setattr(shop_module, 'ask_confirmation', lambda _prompt: True)

        shop._buy(shop.catalog_by_id[1])

        assert shop.player.balance_multiplier == 2
        assert shop.player.balance == 800

    def test_buy_multiplier_cancelled(
        self, shop: Shop, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        shop.player.balance = 1000
        monkeypatch.setattr(shop_module, 'ask_confirmation', lambda _prompt: False)

        shop._buy(shop.catalog_by_id[1])

        assert shop.player.balance_multiplier == 1
        assert shop.player.balance == 1000

    def test_buy_xp_multiplier(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop.player.balance = 1000
        monkeypatch.setattr(shop_module, 'ask_confirmation', lambda _prompt: True)

        shop._buy(shop.catalog_by_id[2])

        assert shop.player.xp_multiplier == 2
        assert shop.player.balance == 800

    def test_buy_mining_increases_level(self, shop: Shop) -> None:
        shop.player.balance = 1000

        shop._buy(shop.catalog_by_id[4])

        assert shop.player.mining_lvl == 1
        assert shop.player.balance == 700

    def test_buy_coffee(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop.player.balance = 1000
        monkeypatch.setattr(shop_module, 'ask_confirmation', lambda _prompt: True)

        shop._buy(shop.catalog_by_id[7])

        assert shop.player.mining_multiplier == 2
        assert shop.player.balance == 300

    def test_buy_coffee_twice(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop.player.balance = 1000
        shop.player.mining_multiplier = 2
        monkeypatch.setattr(shop_module, 'ask_confirmation', lambda _prompt: True)

        shop._buy(shop.catalog_by_id[7])

        assert shop.player.balance == 1000

    def test_business_is_temporarily_removed(self, shop: Shop) -> None:
        shop.player.balance = 5000

        shop._buy(shop.catalog_by_id[8])

        assert shop.player.business is False
        assert shop.player.balance == 5000

    def test_business_not_enough_money(self, shop: Shop) -> None:
        shop.player.balance = 100

        shop._buy(shop.catalog_by_id[8])

        assert shop.player.balance == 100

    def test_buy_secret_case(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop.player.balance = 10_000
        monkeypatch.setattr(shop_module.random, 'choice', lambda _items: 5000)
        monkeypatch.setattr(shop_module.time, 'sleep', lambda _seconds: None)

        shop._buy(shop.catalog_by_id[9])

        assert shop.player.secret_case == 1
        assert shop.player.balance == 12_500

    def test_discount_is_used_when_buying(self, shop: Shop) -> None:
        shop.player.balance = 1000
        shop.ctx.daily.discount_item_id = 3

        shop._buy(shop.catalog_by_id[3])

        assert shop.player.balance == 760

    def test_maxed_item_cannot_be_bought(self, shop: Shop) -> None:
        shop.player.balance_multiplier = 5
        item = shop._build_catalog()[0]

        shop._buy(item)

        assert shop.player.balance_multiplier == 5

    def test_unknown_item_cannot_be_bought(self, shop: Shop) -> None:
        shop._buy(ShopItem(99, 'Неизвестно', 100))

        assert shop.player.balance == 0


class TestReturn:
    def test_return_multiplier(self, shop: Shop) -> None:
        shop.player.balance_multiplier = 5

        shop._return(shop.catalog_by_id[1])

        assert shop.player.balance_multiplier == 1
        assert shop.player.balance == 1500

    def test_return_multiplier_not_maxed(self, shop: Shop) -> None:
        shop.player.balance_multiplier = 4

        shop._return(shop.catalog_by_id[1])

        assert shop.player.balance_multiplier == 4
        assert shop.player.balance == 0

    def test_return_xp_multiplier(self, shop: Shop) -> None:
        shop.player.xp_multiplier = 5

        shop._return(shop.catalog_by_id[2])

        assert shop.player.xp_multiplier == 1
        assert shop.player.balance == 1500

    def test_return_amulet(self, shop: Shop) -> None:
        shop.player.lucky_amulet = True

        shop._return(shop.catalog_by_id[3])

        assert shop.player.lucky_amulet is False
        assert shop.player.balance == 150

    def test_return_amulet_not_bought(self, shop: Shop) -> None:
        shop._return(shop.catalog_by_id[3])

        assert shop.player.balance == 0

    def test_return_mining_low_level_forbidden(self, shop: Shop) -> None:
        shop.player.mining_lvl = 5
        shop.player.balance = 10_000

        shop._return(shop.catalog_by_id[4])

        assert shop.player.mining_lvl == 5
        assert shop.player.balance == 10_000

    def test_return_mining_max_level_forbidden(self, shop: Shop) -> None:
        shop.player.mining_lvl = 10
        shop.player.balance = 5000

        shop._return(shop.catalog_by_id[4])

        assert shop.player.mining_lvl == 10

    def test_return_mining_not_bought(self, shop: Shop) -> None:
        shop._return(shop.catalog_by_id[4])

        assert shop.player.mining_lvl == 0

    def test_return_potion(self, shop: Shop) -> None:
        shop.player.potion_luck = True

        shop._return(shop.catalog_by_id[5])

        assert shop.player.potion_luck is False
        assert shop.player.balance == 250

    def test_return_ticket(self, shop: Shop) -> None:
        shop.player.lucky_ticket = True

        shop._return(shop.catalog_by_id[6])

        assert shop.player.lucky_ticket is False
        assert shop.player.balance == 200

    def test_return_coffee(self, shop: Shop) -> None:
        shop.player.mining_multiplier = 2

        shop._return(shop.catalog_by_id[7])

        assert shop.player.mining_multiplier == 1
        assert shop.player.balance == 350

    def test_return_coffee_not_bought(self, shop: Shop) -> None:
        shop._return(shop.catalog_by_id[7])

        assert shop.player.balance == 0

    def test_return_business(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop.player.business = True
        monkeypatch.setattr(shop_module.time, 'sleep', lambda _seconds: None)

        shop._return(shop.catalog_by_id[8])

        assert shop.player.business is False
        assert shop.player.balance == 600

    def test_return_secret_case_forbidden(self, shop: Shop) -> None:
        shop.player.balance = 100

        shop._return(shop.catalog_by_id[9])

        assert shop.player.balance == 100

    def test_unknown_item_cannot_be_returned(self, shop: Shop) -> None:
        shop._return(ShopItem(99, 'Неизвестно', 100))

        assert shop.player.balance == 0


class TestOpen:
    def test_buy_flow(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop.player.balance = 1000
        monkeypatch.setattr(shop_module.random, 'random', lambda: 0.5)
        monkeypatch.setattr(shop, '_choose_item', lambda: shop.catalog_by_id[3])
        monkeypatch.setattr(shop, '_choose_action', lambda: ShopAction.BUY)

        shop.open()

        assert shop.player.lucky_amulet is True
        assert shop.player.balance == 700

    def test_return_flow(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop.player.lucky_amulet = True
        monkeypatch.setattr(shop_module.random, 'random', lambda: 0.5)
        monkeypatch.setattr(shop, '_choose_item', lambda: shop.catalog_by_id[3])
        monkeypatch.setattr(shop, '_choose_action', lambda: ShopAction.RETURN)

        shop.open()

        assert shop.player.lucky_amulet is False
        assert shop.player.balance == 150

    def test_cancel_item_selection(
        self, shop: Shop, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(shop_module.random, 'random', lambda: 0.5)
        monkeypatch.setattr(shop, '_choose_item', lambda: None)

        shop.open()

        assert shop.player.balance == 0

    def test_cancel_action(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(shop_module.random, 'random', lambda: 0.5)
        monkeypatch.setattr(shop, '_choose_item', lambda: shop.catalog_by_id[3])
        monkeypatch.setattr(shop, '_choose_action', lambda: None)

        shop.open()

        assert shop.player.lucky_amulet is False


def test_shop_action_values() -> None:
    assert ShopAction.BUY == 1
    assert ShopAction.RETURN == 2


def test_shop_daily_is_used_for_discount() -> None:
    ctx = GameContext(player=Player(id=1), db=None, daily=Daily())  # type: ignore[arg-type]
    shop = Shop(ctx)
    ctx.daily.discount_item_id = 3

    assert shop._final_price(shop.catalog_by_id[3]) == 240
