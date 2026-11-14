import pytest

import mini_store.shop as shop_module
from mini_store.models import GameContext
from mini_store.shop import Shop, ShopAction, ShopItem


@pytest.fixture
def shop(ctx: GameContext, monkeypatch: pytest.MonkeyPatch) -> Shop:
    monkeypatch.setattr(shop_module, 'cls', lambda: None)
    return Shop(ctx)


class TestCatalog:
    def test_maxed_items_have_no_price(self, shop: Shop) -> None:
        shop._player.balance_multiplier = 5
        shop._player.xp_multiplier = 5
        shop._player.mining_lvl = 10

        shop._catalog = shop._build_catalog()

        assert shop._catalog_by_id[0].price is None
        assert shop._catalog_by_id[1].price is None
        assert shop._catalog_by_id[3].price is None

    def test_names_include_current_multiplier(self, shop: Shop) -> None:
        shop._player.balance_multiplier = 3
        shop._player.xp_multiplier = 4

        shop._catalog = shop._build_catalog()

        assert shop._catalog[0].name == 'Множитель монет 3x'
        assert shop._catalog[1].name == 'Множитель опыта 4x'

    def test_catalog_is_indexed_by_id(self, shop: Shop) -> None:
        assert shop._catalog_by_id[0].name == next(
            item.name for item in shop._catalog if item.id == 0
        )


class TestPriceLabels:
    def test_regular_price(self, shop: Shop) -> None:
        assert shop._price_label(shop._catalog_by_id[3]) == '300 монет'

    def test_max_price(self, shop: Shop) -> None:
        shop._player.balance_multiplier = 5
        item = shop._build_catalog()[0]

        assert 'MAX' in shop._price_label(item)

    def test_discount_label(self, shop: Shop) -> None:
        shop._ctx.daily.discount_item_id = 3
        label = shop._price_label(shop._catalog_by_id[3])

        assert '300' in label
        assert '240' in label
        assert 'СКИДКА' in label

    def test_final_price_without_discount(self, shop: Shop) -> None:
        assert shop._final_price(shop._catalog_by_id[3]) == 300

    def test_final_price_with_discount(self, shop: Shop) -> None:
        shop._ctx.daily.discount_item_id = 5

        assert shop._final_price(shop._catalog_by_id[5]) == 320


class TestDiscount:
    def test_no_discount(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop._ctx.daily.discount_item_id = 3
        monkeypatch.setattr(shop_module.random, 'random', lambda: 0.5)

        shop._roll_discount()

        assert shop._ctx.daily.discount_item_id is None

    def test_discount_is_applied(
        self,
        shop: Shop,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        monkeypatch.setattr(shop_module.random, 'random', lambda: 0.1)
        monkeypatch.setattr(shop_module.random, 'choice', lambda _items: shop._catalog_by_id[7])

        shop._roll_discount()

        assert shop._ctx.daily.discount_item_id == 7
        assert 'Секретный кейс' in capsys.readouterr().out


class TestBuy:
    def test_buy_unique_item(self, shop: Shop) -> None:
        shop._player.balance = 1000

        shop._buy(shop._catalog_by_id[2])

        assert shop._player.lucky_amulet is True
        assert shop._player.balance == 700

    def test_cannot_buy_unique_item_twice(self, shop: Shop) -> None:
        shop._player.balance = 1000
        shop._player.lucky_amulet = True

        shop._buy(shop._catalog_by_id[2])

        assert shop._player.balance == 1000

    def test_not_enough_money(self, shop: Shop) -> None:
        shop._player.balance = 100

        shop._buy(shop._catalog_by_id[3])

        assert shop._player.lucky_amulet is False
        assert shop._player.balance == 100

    def test_buy_multiplier_with_confirmation(
        self, shop: Shop, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        shop._player.balance = 1000
        monkeypatch.setattr(shop_module, 'ask_confirmation', lambda _prompt: True)

        shop._buy(shop._catalog_by_id[0])

        assert shop._player.balance_multiplier == 2
        assert shop._player.balance == 800

    def test_buy_multiplier_cancelled(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop._player.balance = 1000
        monkeypatch.setattr(shop_module, 'ask_confirmation', lambda _prompt: False)

        shop._buy(shop._catalog_by_id[0])

        assert shop._player.balance_multiplier == 1
        assert shop._player.balance == 1000

    def test_buy_xp_multiplier(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop._player.balance = 1000
        monkeypatch.setattr(shop_module, 'ask_confirmation', lambda _prompt: True)

        shop._buy(shop._catalog_by_id[1])

        assert shop._player.xp_multiplier == 2
        assert shop._player.balance == 800

    def test_buy_mining_increases_level(self, shop: Shop) -> None:
        shop._player.balance = 1000

        shop._buy(shop._catalog_by_id[3])

        assert shop._player.mining_lvl == 1
        assert shop._player.balance == 700

    def test_buy_coffee(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop._player.mining_lvl = 1
        shop._player.balance = 1000
        shop._catalog = shop._build_catalog()
        monkeypatch.setattr(shop_module, 'ask_confirmation', lambda _prompt: True)

        shop._buy(shop._catalog_by_id[6])

        assert shop._player.has_coffee is True
        assert shop._player.balance == 300

    def test_buy_coffee_twice(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop._player.balance = 1000
        shop._player.has_coffee = True
        shop._catalog = shop._build_catalog()
        monkeypatch.setattr(shop_module, 'ask_confirmation', lambda _prompt: True)

        with pytest.raises(
            KeyError
        ):  # because if player buys coffee once, it won't even be in catalog.
            shop._buy(shop._catalog_by_id[6])

        assert shop._player.balance == 1000

    def test_buy_secret_case(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop._player.balance = 10_000
        monkeypatch.setattr(shop_module.random, 'choice', lambda _items: 5000)
        monkeypatch.setattr(shop_module.time, 'sleep', lambda _seconds: None)

        shop._buy(shop._catalog_by_id[7])

        assert shop._player.balance == 12_500

    def test_discount_is_used_when_buying(self, shop: Shop) -> None:
        shop._player.balance = 1000
        shop._ctx.daily.discount_item_id = 3

        shop._buy(shop._catalog_by_id[3])

        assert shop._player.balance == 760

    def test_maxed_item_cannot_be_bought(self, shop: Shop) -> None:
        shop._player.balance_multiplier = 5
        item = shop._build_catalog()[0]

        shop._buy(item)

        assert shop._player.balance_multiplier == 5


class TestReturn:
    def test_return_multiplier(self, shop: Shop) -> None:
        shop._player.balance_multiplier = 5

        shop._return(shop._catalog_by_id[0])

        assert shop._player.balance == 1500
        assert shop._player.balance_multiplier == 1

    def test_return_multiplier_not_maxed(self, shop: Shop) -> None:
        shop._player.balance_multiplier = 4

        shop._return(shop._catalog_by_id[0])

        assert shop._player.balance == 0
        assert shop._player.balance_multiplier == 4

    def test_return_xp_multiplier(self, shop: Shop) -> None:
        shop._player.xp_multiplier = 5

        shop._return(shop._catalog_by_id[1])

        assert shop._player.balance == 1500
        assert shop._player.xp_multiplier == 1

    def test_return_amulet(self, shop: Shop) -> None:
        shop._player.lucky_amulet = True

        shop._return(shop._catalog_by_id[2])

        assert shop._player.balance == 150
        assert shop._player.lucky_amulet is False

    def test_return_amulet_not_bought(self, shop: Shop) -> None:
        shop._return(shop._catalog_by_id[2])

        assert shop._player.balance == 0

    def test_return_mining_low_level_forbidden(self, shop: Shop) -> None:
        shop._player.mining_lvl = 5
        shop._player.balance = 10_000

        shop._return(shop._catalog_by_id[3])

        assert shop._player.balance == 10_000
        assert shop._player.mining_lvl == 5

    def test_return_mining_max_level_forbidden(self, shop: Shop) -> None:
        shop._player.mining_lvl = 10
        shop._player.balance = 5000

        shop._return(shop._catalog_by_id[3])

        assert shop._player.mining_lvl == 10

    def test_return_mining_not_bought(self, shop: Shop) -> None:
        shop._return(shop._catalog_by_id[3])

        assert shop._player.mining_lvl == 0

    def test_return_potion(self, shop: Shop) -> None:
        shop._player.potion_luck = True

        shop._return(shop._catalog_by_id[4])

        assert shop._player.balance == 250
        assert shop._player.potion_luck is False

    def test_return_ticket(self, shop: Shop) -> None:
        shop._player.lucky_ticket = True

        shop._return(shop._catalog_by_id[5])

        assert shop._player.balance == 200
        assert shop._player.lucky_ticket is False

    def test_return_coffee(self, shop: Shop) -> None:
        shop._player.mining_lvl = 1
        shop._player.has_coffee = True
        shop._catalog = shop._build_catalog()

        shop._return(shop._catalog_by_id[6])

        assert shop._player.balance == 350
        assert shop._player.has_coffee is False

    def test_return_coffee_not_bought(self, shop: Shop, capsys: pytest.CaptureFixture[str]) -> None:
        shop._player.mining_lvl = 1
        shop._catalog = shop._build_catalog()

        shop._return(shop._catalog_by_id[6])

        assert 'У вас не куплено "Кофе"' in capsys.readouterr().out
        assert shop._player.balance == 0
        assert shop._player.has_coffee is False

    def test_return_secret_case_forbidden(
        self, shop: Shop, capsys: pytest.CaptureFixture[str]
    ) -> None:
        shop._return(shop._catalog_by_id[7])

        assert 'Секретный кейс нельзя вернуть!' in capsys.readouterr().out
        assert shop._player.balance == 0


class TestOpen:
    def test_buy_flow(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop._player.balance = 1000
        monkeypatch.setattr(shop_module.random, 'random', lambda: 0.5)
        monkeypatch.setattr(shop, '_choose_item', lambda: shop._catalog_by_id[2])
        monkeypatch.setattr(shop, '_choose_action', lambda: ShopAction.BUY)

        shop.open()

        assert shop._player.balance == 700
        assert shop._player.lucky_amulet is True

    def test_return_flow(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        shop._player.lucky_amulet = True
        monkeypatch.setattr(shop_module.random, 'random', lambda: 0.5)
        monkeypatch.setattr(shop, '_choose_item', lambda: shop._catalog_by_id[2])
        monkeypatch.setattr(shop, '_choose_action', lambda: ShopAction.RETURN)

        shop.open()

        assert shop._player.balance == 150
        assert shop._player.lucky_amulet is False

    def test_cancel_item_selection(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(shop_module.random, 'random', lambda: 0.5)
        monkeypatch.setattr(shop, '_choose_item', lambda: None)

        shop.open()

        assert shop._player.balance == 0

    def test_cancel_action(self, shop: Shop, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(shop_module.random, 'random', lambda: 0.5)
        monkeypatch.setattr(shop, '_choose_item', lambda: shop._catalog_by_id[2])
        monkeypatch.setattr(shop, '_choose_action', lambda: None)

        shop.open()

        assert shop._player.lucky_amulet is False


def test_shop_action_values() -> None:
    assert ShopAction.BUY == 1
    assert ShopAction.RETURN == 2


def test_shop_daily_is_used_for_discount(shop: Shop) -> None:
    shop._ctx.daily.discount_item_id = 3

    assert shop._final_price(shop._catalog_by_id[3]) == 240


class TestDiscountPersistence:
    @pytest.mark.xfail(reason='TODO in next update')
    def test_new_shop_does_not_reroll_discount(
        self,
        ctx: GameContext,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        first = Shop(ctx)
        monkeypatch.setattr(shop_module.random, 'random', lambda: 0.1)
        monkeypatch.setattr(shop_module.random, 'choice', lambda _items: first._catalog_by_id[3])

        first._roll_discount()

        assert ctx.daily.discount_item_id == 3

        second = Shop(ctx)
        monkeypatch.setattr(shop_module.random, 'choice', lambda _items: second._catalog_by_id[5])

        second._roll_discount()

        assert ctx.daily.discount_item_id == 3

    def test_discount_skips_unavailable_items(
        self,
        shop: Shop,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        shop._player.balance_multiplier = 5
        shop._player.xp_multiplier = 5
        shop._player.mining_lvl = 10
        shop._catalog = shop._build_catalog()

        offered: list[ShopItem] = []

        def choose(items: list[ShopItem]) -> ShopItem:
            offered.extend(items)
            return items[0]

        monkeypatch.setattr(shop_module.random, 'random', lambda: 0.1)
        monkeypatch.setattr(shop_module.random, 'choice', choose)

        shop._roll_discount()

        assert offered
        assert all(item.price is not None for item in offered)
