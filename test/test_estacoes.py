from backend import metro

from requests import Session


def test_list_estacoes():
    estacoes = metro.list_estacoes(
        [
            "https://pt.wikipedia.org/wiki/Metr%C3%B4_do_Rio_de_Janeiro",
            "https://pt.wikipedia.org/wiki/SuperVia",
        ]
    )

    assert len(estacoes) > 200

    with Session() as session:
        info_estacoes = [metro.fetch(session, list(estacoes)[i][1]) for i in range(10)]

    assert len(info_estacoes) == 10
    assert len(info_estacoes[0]) == 3

    estacao, lat, long = info_estacoes[0]
    assert isinstance(estacao, str)
    assert isinstance(lat, float)
    assert isinstance(long, float)
