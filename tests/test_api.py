from sdpb.api import get_network_collection_rep, get_variable_collection_rep


def test_network_collection(network_session, tst_networks):
    result = sorted(
        get_network_collection_rep(network_session),
        key=lambda r: r['id']
    )
    assert len(result) == len(tst_networks)
    assert result == [
        {
            'id': nw.id,
            'name': nw.name,
            'long_name': nw.long_name,
            'virtual': nw.virtual,
            'color': nw.color,
            'uri': '/networks/{}'.format(nw.id),
        }
        for nw in tst_networks
    ]


def test_variable_collection(variable_session, tst_variables):
    result = sorted(
        get_variable_collection_rep(variable_session),
        key=lambda r: r['id']
    )
    assert len(result) == len(tst_variables)
    assert result == [
        {
            'id': var.id,
            'name': var.name,
            'display_name': var.display_name,
            'short_name': var.short_name,
            'standard_name': var.standard_name,
            'cell_method': var.cell_method,
            'unit': var.unit,
            'precision': var.precision,
            'uri': '/variables/{}'.format(var.id),
            'network_uri': '/networks/{}'.format(var.network.id),
        }
        for var in tst_variables
    ]
