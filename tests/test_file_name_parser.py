from scripts.utils import parse_reseller_file_name

def test_parse_file():
    m = parse_reseller_file_name('DailySales_02012020_R001.csv')
    assert str(m['sale_date']) == '2020-02-01'
    assert m['reseller_id'] == 'R001'
