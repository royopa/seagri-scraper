import requests


def test_pagination():
    pages = (
        'http://www.seagri.ba.gov.br/',
        'http://www.seagri.ba.gov.br/cotacao'
    )

    for page in pages:
        r = requests.get(page)
        assert r.status_code is 200

