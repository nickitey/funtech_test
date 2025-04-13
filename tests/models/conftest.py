class _TestModelAttrs:
    @property
    def model(self):
        raise NotImplementedError(
            "Значением свойства model должен быть класс тестируемой модели"
        )

    def test_model_attrs(self, field, type, params):
        model_name = self.model.__name__
        assert hasattr(
            self.model, field
        ), f"В модели `{model_name}` укажите атрибут `{field}`."
        model_field = self.model._meta.get_field(field)
        assert isinstance(model_field, type), (
            f"В модели `{model_name}` у атрибута `{field}` "
            f"укажите тип `{type}`."
        )
        for param, value_param in params.items():
            hasattr(model_field, param)
            assert hasattr(model_field, param), (
                f"В модели `{model_name}` для атрибута `{field}` "
                f"укажите параметр `{param}`."
            )
            assert getattr(model_field, param) == value_param, (
                f"В модели `{model_name}` в атрибуте `{field}` "
                f"проверьте значение параметра `{param}` "
                "на соответствие заданию."
            )
