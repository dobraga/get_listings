import logging
from joblib import load
from os.path import join, abspath

from backend.timeit import timeit
from dashboard.models import Imovel
from backend.preprocess import preprocess
from backend.get_activated_listings import get_activated_listings

log = logging.getLogger(__name__)

model_file = abspath(join(".", "data", "model.pkl"))
model_file = abspath(join(__file__, "..", "..", "data", "model.pkl"))
log.info(f"Loading model in {model_file}")
model = load(model_file)


def update_predict(db, locationId, business_type, listing_type) -> None:
    df = get_activated_listings(db.engine, locationId, business_type, listing_type)

    if df.empty:
        log.warning(
            f"Nenhum imóvel encontrado {locationId=} {business_type=} {listing_type=}"
        )
    else:
        X, _ = preprocess(df)

        with timeit("Atualização da previsão de preços", log, "info"):
            df["pred"] = model.predict(X)
            for _, (url, pred) in df[["url", "pred"]].iterrows():
                log.debug(f"Atualizando a previsão de '{url}' para {pred}")
                Imovel.query.filter_by(url=url).first().total_fee_predict = pred

            db.session.commit()


if __name__ == "__main__":
    from sqlalchemy import create_engine

    from backend.settings import settings

    locationId = "BR>Rio de Janeiro>NULL>Rio de Janeiro>Zona Norte>Tijuca"
    business_type = "RENTAL"
    listing_type = "USED"

    db = create_engine(settings["SQLALCHEMY_DATABASE_URI"])
