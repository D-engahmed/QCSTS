from django.test import Client, SimpleTestCase, override_settings


class FrontendCorsTests(SimpleTestCase):
    @override_settings(
        CORS_ALLOWED_ORIGINS=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        CORS_ALLOW_CREDENTIALS=True,
    )
    def test_nextjs_origin_can_preflight_auth_registration(self):
        response = Client().options(
            "/api/v1/auth/register/",
            HTTP_ORIGIN="http://localhost:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type,authorization",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Origin"),
            "http://localhost:3000",
        )
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Credentials"),
            "true",
        )
