from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from delivery.core.celery_app import celery_app
from delivery.core.di.parcels import get_parcel_service
from delivery.parcel_types.api.router import get_service as get_pt_service  # реюз DI
from delivery.parcel_types.services.service import ParcelTypeService
from delivery.parcels.services.service import ParcelService

router = APIRouter(tags=["ui"])


def _page(body: str) -> HTMLResponse:
    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Delivery UI</title>
        <style>
          body {{ font-family: sans-serif; margin: 24px; }}
          form {{ margin-bottom: 18px; padding: 12px; border: 1px solid #ddd; border-radius: 8px; }}
          table {{ border-collapse: collapse; width: 100%; }}
          th, td {{ border: 1px solid #ddd; padding: 8px; }}
          th {{ text-align: left; }}
          .muted {{ color: #666; }}
        </style>
      </head>
      <body>
        <h1>Delivery Service</h1>
        {body}
      </body>
    </html>
    """
    return HTMLResponse(html)


@router.get("/ui", response_class=HTMLResponse)
async def ui_home(
    request: Request,
    pt_service: ParcelTypeService = Depends(get_pt_service),
    parcel_service: ParcelService = Depends(get_parcel_service),
) -> HTMLResponse:
    # список типов
    types = await pt_service.list_types()

    # список посылок этой сессии
    session_id = request.state.session_id
    parcels = await parcel_service.list_parcels(
        session_id=session_id, limit=100, offset=0, parcel_type_code=None, has_cost=None
    )

    options = "\n".join([f'<option value="{t.code}">{t.code} — {t.name}</option>' for t in types])

    rows = []
    for p in parcels:
        cost = p.delivery_cost_rub if p.delivery_cost_rub is not None else "Не рассчитано"
        rows.append(
            f"<tr>"
            f"<td>{p.id}</td>"
            f"<td>{p.title}</td>"
            f"<td>{p.parcel_type_code}</td>"
            f"<td>{p.weight_kg}</td>"
            f"<td>{p.content_usd}</td>"
            f"<td>{cost}</td>"
            f"</tr>"
        )
    table = (
        "<table>"
        "<thead><tr><th>ID</th><th>Title</th><th>Type</th><th>Weight</th>"
        "<th>Content USD</th><th>Delivery RUB</th></tr></thead>"
        f"<tbody>{''.join(rows) if rows else '<tr><td colspan=6 class=muted>Пока пусто</td></tr>'}"
        f"</tbody>"
        "</table>"
    )

    body = f"""
    <form method="post" action="/ui/parcel-types">
      <h3>Создать тип посылки</h3>
      <input name="code" placeholder="DOC" required maxlength="32" />
      <input name="name" placeholder="Documents" required maxlength="128" />
      <input name="base_price_usd" placeholder="5.00" required />
      <input name="price_per_kg_usd" placeholder="2.50" required />
      <button type="submit">Создать</button>
    </form>

    <form method="post" action="/ui/parcels">
      <h3>Создать посылку</h3>
      <input name="title" placeholder="Название" required maxlength="256" />
      <select name="parcel_type_code" required>
        {options}
      </select>
      <input name="weight_kg" placeholder="2" required />
      <input name="content_usd" placeholder="100.00" required />
      <button type="submit">Создать</button>
    </form>

    <form method="post" action="/ui/refresh-costs">
      <button type="submit">Рассчитать стоимость</button>
    </form>

    <h2>Мои посылки</h2>
    {table}
    """
    return _page(body)


@router.post("/ui/parcel-types")
async def ui_create_type(
    code: str = Form(...),
    name: str = Form(...),
    base_price_usd: str = Form(...),
    price_per_kg_usd: str = Form(...),
    pt_service: ParcelTypeService = Depends(get_pt_service),
):
    await pt_service.create_type(
        code=code,
        name=name,
        base_price_usd=base_price_usd,
        price_per_kg_usd=price_per_kg_usd,
    )
    return RedirectResponse("/ui", status_code=303)


@router.post("/ui/parcels")
async def ui_create_parcel(
    request: Request,
    title: str = Form(...),
    parcel_type_code: str = Form(...),
    weight_kg: float = Form(...),
    content_usd: str = Form(...),
    parcel_service: ParcelService = Depends(get_parcel_service),
):
    await parcel_service.create_parcel(
        session_id=request.state.session_id,
        parcel_type_code=parcel_type_code,
        title=title,
        weight_kg=weight_kg,
        content_usd=content_usd,
    )
    return RedirectResponse("/ui", status_code=303)


@router.post("/ui/refresh-costs")
async def ui_refresh_costs():
    celery_app.send_task("parcels.refresh_delivery_costs", args=(500,))
    return RedirectResponse("/ui", status_code=303)
