from dashboard.components.carousel import carousel

import locale


locale.setlocale(locale.LC_ALL, "pt_BR.utf8")


style_left = "float: left; width: 40%; height: 100%"
style_right = "cursor: pointer; float: right; width: 58%; height: 100%"
style_text = "white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"


def to_currency(value):
    return locale.currency(value, grouping=True, symbol=True)


def box(**kwargs) -> str:
    if kwargs["business_type"] == "RENTAL":

        if kwargs["condo_fee"] > 0:
            preco = """
            <p>
                <span> Valor {price}/Mês |</span>
                <span> Valor Condomínio {condo_fee}/Mês |</span>
                <span> total {total_fee}/Mês </span>
            </p>
            """.format(
                price=to_currency(kwargs["price"]),
                condo_fee=to_currency(kwargs["condo_fee"]),
                total_fee=to_currency(kwargs["total_fee"]),
            )
        else:
            preco = """
            <p><span> Valor {}/Mês</span></p>
            """.format(
                to_currency(kwargs["price"])
            )
    else:
        preco = """
        <p>
            <span> Valor {price} |</span>
            <span> Valor Condomínio {condo_fee}/Mês |</span>
            <span> total {price} </span>
        </p>
        """.format(
            price=to_currency(kwargs["price"]),
            condo_fee=to_currency(kwargs["condo_fee"]),
        )

    images = kwargs["images"]
    if images is not None and isinstance(images, list) and len(images) > 0:
        images = carousel(*images)
    else:
        images = "https://img2.gratispng.com/20180407/yhw/kisspng-empty-set-null-set-symbol-mathematics-forbidden-5ac859ad09c119.24223671152307959704.jpg"

    return """
    <div style="width: 40vw; height: 20vh;">
        <div style="{style_left}">
            {images}
        </div>

        <div style="{style_right}" onclick="window.open('{url}');">
            <div style="width: 100%;">
                <div title="{address}" style = "{style_text}"> {address} </div>
                <p title="{title}" style = "{style_text}"> {title} </p>
                {preco}
                <p style = "{style_text}" title="{amenities}"> {amenities} </p>
            </div>
        </div>
    </div>
    """.format(
        url=kwargs["url"],
        address=kwargs["address"],
        title=kwargs["title"],
        amenities=kwargs["amenities"],
        style_left=style_left,
        style_right=style_right,
        style_text=style_text,
        images=images,
        preco=preco,
    )
