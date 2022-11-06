from typing import Optional

from starlette.requests import Request

from app.models.ml import MLModelCreate
from app.models.validation_error import ValidationError
from app.services import ml_service
from app.viewmodels.shared.viewmodel import ViewModelBase


class AddMLViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.name: Optional[str] = None
        self.url: Optional[str] = None

    async def post_form(self):
        form = await self.request.form()
        self.name = form.get('name')
        self.url = form.get('url')

        if not self.name or not self.name.strip():
            self.error = "A model name is required."
        elif not self.url or not self.url.strip():
            self.error = "A model URL is required."
        else:
            # Try to add the model catch any errors
            try:
                _ = await ml_service.add_ml_model(
                    ml_model=MLModelCreate(model_name=self.name, model_url=self.url),
                    bearer_token=self.bearer_token
                )
            except ValidationError as e:
                self.error = e.error_msg
