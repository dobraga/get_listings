import logging
import pandas as pd
from joblib import load
from os.path import join, abspath

from backend.preprocess import preprocess

from dashboard.models import Imovel
from dashboard.extensions.serializer import ImovelSchema

log = logging.getLogger(__name__)
IS = ImovelSchema(many=True)

model_file = abspath(join(__file__, "..", "..", "data", "model.pkl"))
log.info(f"Loading model in {model_file}")
model = load(model_file)


def update_predict(db, locationId, business_type, listing_type) -> None:
    log.info("Atualizando previsão de preços")

    imoveis = db.engine.execute(
        f"""
        SELECT *
        FROM imovel
        WHERE
            listing_type = '{listing_type}'
            and business_type = '{business_type}'
            and location_id = '{locationId}'
    """
    ).all()

    if imoveis:
        df = pd.DataFrame(IS.dump(imoveis))

        X, _ = preprocess(df)
        log.info(f"shape: {X.shape}, columns: {X.columns.tolist()}")
        df["pred"] = model.predict(X)

        for _, (url, pred) in df[["url", "pred"]].iterrows():
            log.debug(f"Atualizando a previsão de '{url}' para {pred}")
            Imovel.query.filter_by(url=url).first().total_fee_predict = pred

        db.session.commit()
    else:
        log.info("Nenhum imóvel encontrado")

    log.info("Atualização da previsão de preços finalizada")
