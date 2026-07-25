from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from use import pred

# список вопросов для опросника
QUESTIONS = [
    "1. У нас с супругом схожие представления о том, как проводить досуг.",
    "2. Я знаю, что мы можем не зацикливаться на разногласиях, даже когда возникают трудности.",
    "3. При необходимости, я думаю, мы можем вернуться к началу разговора и всё исправить.",
    "4. Когда я обсуждаю что-то с партнёром, попытки наладить контакт в конечном счёте приносят результат.",
    "5. Время, проведённое с партнёром, для нас по-особому ценно.",
    "6. У нас с супругом схожие взгляды на личную свободу.",
    "7. Мы с супругом сходимся во мнении о том, какой должна быть любовь.",
    "8. Мне нравится проводить праздники с партнёром.",
    "9. Мне нравится путешествовать/гулять с партнёром.",
    "10. У нас с партнёром большинство интересов — общие.",
]

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# гет запрос
@app.get("/", response_class=HTMLResponse)
async def form(request: Request):
    return templates.TemplateResponse(request=request, name="form.html")



# пост запрос
@app.post("/submit", response_class=HTMLResponse)
async def facts(
    request: Request,
    gender_1: int = Form(...),
    income_1: int = Form(...),
    children_1: int = Form(...),
    age_1: int = Form(...),
    attractiveness_1: int = Form(...),
    gender_2: int = Form(...),
    income_2: int = Form(...),
    children_2: int = Form(...),
    age_2: int = Form(...),
    attractiveness_2: int = Form(...),
):


    partner1 = pred(gender_1, income_1, children_1, age_1, attractiveness_1)
    partner2 = pred(gender_2, income_2, children_2, age_2, attractiveness_2)



    return templates.TemplateResponse(
        request=request,
        name="partner_choice.html",
        context={
            "partner1": partner1,
            "partner2": partner2,
            "age_1": age_1,
            "age_2": age_2,
        }
    )




# пост запрос номер два
@app.post("/start-test", response_class=HTMLResponse)
async def start_test(
    request: Request,
    partner1: int = Form(...),
    partner2: int = Form(...),
    age_1: int = Form(...),
    age_2: int = Form(...),
    current_partner: int = Form(...),
    test_p1: str = Form(""),
    test_p2: str = Form(""),
):


    return templates.TemplateResponse(
        request=request,
        name="test.html",
        context={
            "questions": QUESTIONS,
            "partner1": partner1,
            "partner2": partner2,
            "age_1": age_1,
            "age_2": age_2,
            "current_partner": current_partner,
            "test_p1": test_p1,
            "test_p2": test_p2,
        }
    )

# пост запрос с вопросами партнеру один и партнеру два
@app.post("/submit-test", response_class=HTMLResponse)
async def submit_test(
    request: Request,
    partner1: int = Form(...),
    partner2: int = Form(...),
    age_1: int = Form(...),
    age_2: int = Form(...),
    current_partner: int = Form(...),
    q0: int = Form(...),
    q1: int = Form(...),
    q2: int = Form(...),
    q3: int = Form(...),
    q4: int = Form(...),
    q5: int = Form(...),
    q6: int = Form(...),
    q7: int = Form(...),
    q8: int = Form(...),
    q9: int = Form(...),
    test_p1: str = Form(""),
    test_p2: str = Form(""),
):
    test_total = q0 + q1 + q2 + q3 + q4 + q5 + q6 + q7 + q8 + q9

    if current_partner == 1:
        test_p1 = str(test_total)
    else:
        test_p2 = str(test_total)

    if test_p1 and test_p2:
        return _show_results(request, partner1, partner2, age_1, age_2, int(test_p1), int(test_p2))

    missing_partner = 2 if not test_p2 else 1

    return templates.TemplateResponse(
        request=request,
        name="next_step.html",
        context={
            "partner1": partner1,
            "partner2": partner2,
            "age_1": age_1,
            "age_2": age_2,
            "test_p1": test_p1,
            "test_p2": test_p2,
            "missing_partner": missing_partner,
        }
    )


@app.post("/next-step", response_class=HTMLResponse)
async def next_step(
    request: Request,
    partner1: int = Form(...),
    partner2: int = Form(...),
    age_1: int = Form(...),
    age_2: int = Form(...),
    test_p1: str = Form(""),
    test_p2: str = Form(""),
    action: str = Form(...),
    missing_partner: int = Form(...),
):
    if action == "call":
        return templates.TemplateResponse(
            request=request,
            name="test.html",
            context={
                "questions": QUESTIONS,
                "partner1": partner1,
                "partner2": partner2,
                "age_1": age_1,
                "age_2": age_2,
                "current_partner": missing_partner,
                "test_p1": test_p1,
                "test_p2": test_p2,
            }
        )

    if missing_partner == 1:
        partner1 += 20
        test_p1_val = int(test_p1) if test_p1 else 0
        test_p2_val = int(test_p2) if test_p2 else 0
    else:
        partner2 += 20
        test_p1_val = int(test_p1) if test_p1 else 0
        test_p2_val = int(test_p2) if test_p2 else 0

    return _show_results(request, partner1, partner2, age_1, age_2, test_p1_val, test_p2_val)


def _show_results(
    request: Request,
    partner1: int,
    partner2: int,
    age_1: int,
    age_2: int,
    test_p1: int,
    test_p2: int,
) -> HTMLResponse:
    partner1_total = partner1 + test_p1
    partner2_total = partner2 + test_p2

    summa = partner1_total + partner2_total

    if abs(age_1 - age_2) >= 10:
        summa -= 20

    if abs(partner1_total - partner2_total) >= 60 and abs(partner1_total - partner2_total) <= 101:
        summa -= 100


    if 140 <= summa <= 200:
        my_message = "Ваши отношения (возможно) продлятся больше 1 года"
    elif 201 <= summa <= 250:
        my_message = "Ваши отношения (возможно) продлятся 2-3 года"
    elif 251 <= summa <= 300:
        my_message = "Ваши отношения (возможно) продлятся 3-5 лет"
    elif summa >= 301:
        my_message = "Ваши отношения (возможно) продлятся больше 5 лет"
    elif abs(partner1_total - partner2_total) >= 102:
        my_message = "К сожалению, определенный прогноз дать сложно."
    else:
        my_message = "К сожалению, определенный прогноз дать сложно."

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "message": my_message,
            "partner1": partner1_total,
            "partner2": partner2_total,
        }
    )
