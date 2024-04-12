import inspect


def grey_out_pending(rows):
    """
    TODO: implement this function
    Manually build html table using this as a template:
    """
    print(f"{__name__}.{inspect.stack()[0][3]}")

    top = """
    <table>
        <thead>
        <tr><th>Account     </th><th>Product       </th><th style="text-align: right;">  Amount</th><th style="text-align: right;">  Change</th></tr>
    </thead>
        <tbody>
    """
    body = """
        <tr><td>Solomon High</td><td>Stargate token</td><td style="text-align: right;">     737</td><td style="text-align: right;">     -60</td></tr>
        <tr><td>Solomon High</td><td>Grizzly token </td><td style="text-align: right;">      43</td><td style="text-align: right;">      -1</td></tr>
        <tr><td>Solomon High</td><td>Synapse Token </td><td style="text-align: right;">    2126</td><td style="text-align: right;">    -243</td></tr>
    """
    bottom = """
    </tbody>
        </table>
    """
    html = top + body + bottom
    # print(html)
    return html
