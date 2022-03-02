style = """
    .carousel {
        width: 100%;
        height: 100%;
    }

    ul.slides {
        display: block;
        height: 100%;
        margin: 0;
        padding: 0;
        overflow: hidden;
        list-style: none;
    }

    .slides * {
        user-select: none;
        -ms-user-select: none;
        -moz-user-select: none;
        -khtml-user-select: none;
        -webkit-user-select: none;
        -webkit-touch-callout: none;
    }

    ul.slides input {
        display: none;
    }


    .slide-container {
        display: block;
    }

    .slide-image {
        display: block;
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        opacity: 0;
        transition: all .7s ease-in-out;
    }

    .carousel-controls {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
        font-size: 100px;
        line-height: 600px;
        color: #fff;
    }

    .carousel-controls label {
        display: none;
        position: absolute;
        padding: 0 20px;
        opacity: 0;
        transition: opacity .2s;
        cursor: pointer;
    }

    .slide-image:hover+.carousel-controls label {
        opacity: 0.5;
    }

    .carousel-controls label:hover {
        opacity: 1;
    }

    .carousel-controls .prev-slide {
        width: 49%;
        text-align: left;
        left: 0;
    }

    .carousel-controls .next-slide {
        width: 49%;
        text-align: right;
        right: 0;
    }

    input:checked+.slide-container .slide-image {
        opacity: 1;
        transform: scale(1);
        transition: opacity 1s ease-in-out;
    }

    .slide-image img {
        width: auto;
        min-width: 100%;
        height: 100%;
    }

    input:checked+.slide-container .carousel-controls label {
        display: block;
    }

    input#img-1:checked~.carousel-dots label#img-dot-1,
    input#img-2:checked~.carousel-dots label#img-dot-2,
    input#img-3:checked~.carousel-dots label#img-dot-3,
    input#img-4:checked~.carousel-dots label#img-dot-4,
    input#img-5:checked~.carousel-dots label#img-dot-5,
    input#img-6:checked~.carousel-dots label#img-dot-6 {
        opacity: 1;
    }
"""

base_layout = """
    <style>
        {style}
    </style>
    <div class="carousel">
        <ul class="slides">
            {elements}
        </ul>
    </div>
"""

element_layout = """
    <input type="radio" name="radio-buttons" id="img-{i}" {checked} />
    <li class="slide-container">
        <div class="slide-image">
        <img src="{image}">
        </div>
        <div class="carousel-controls">
        <label for="img-{prev}" class="prev-slide">
            <span>&lsaquo;</span>
        </label>
        <label for="img-{next}" class="next-slide">
            <span>&rsaquo;</span>
        </label>
        </div>
    </li>
"""


def carousel(*args):
    qtd = len(args)

    elements = []
    for i in range(qtd):
        prev_element = i - 1
        if prev_element < 0:
            prev_element = qtd - 1

        next_element = i + 1
        if next_element > qtd - 1:
            next_element = 0

        checked = "checked" if i == 0 else ""
        element = element_layout.format(
            i=i, image=args[i], prev=prev_element, next=next_element, checked=checked
        )
        elements.append(element)

    elements = "\n".join(elements)

    return base_layout.format(style=style, elements=elements)


if __name__ == "__main__":
    ui = carousel(
        *[
            "https://resizedimgs.vivareal.com/crop/264x200/vr.images.sp/28d553ac978bf30911fb5182ef5db906.jpg",
            "https://resizedimgs.vivareal.com/crop/264x200/vr.images.sp/c11087beeaabbb375e0d631ba9807fdb.jpg",
            "https://resizedimgs.vivareal.com/crop/264x200/vr.images.sp/2e3f439d81eff9cd8071a72f1e6737e4.jpg",
            "https://resizedimgs.vivareal.com/crop/264x200/vr.images.sp/40ea2b948e9f043d8578a6182bc01cb1.jpg",
            "https://resizedimgs.vivareal.com/crop/264x200/vr.images.sp/79ad0fe175edecda2bb742da3f82ffea.jpg",
            "https://resizedimgs.vivareal.com/crop/264x200/vr.images.sp/2a0bb4546301a8b1d0693a29f34bc937.jpg",
        ]
    )
    print(ui)
