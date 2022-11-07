old_sql = """
    select p.product_id, p.descr as product, p.chain, p.project, p.html_label, p.html_table_columns
    ac.account_id
    from actual_total tot
    inner join product p
    on p.product_id=tot.product_id
    inner join account ac
    on ac.account_id=tot.account_id
    where tot.seq=
        (select max(seq) from actual_total
        where product_id=tot.product_id
                and account_id=tot.account_id)
        
    and tot.status='A'
    and p.data_source='HTML'
    and ac.account_id=?
    """
