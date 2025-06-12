from modules.auth.model import Usuario, Dispositivo

from modules.util.math import SMALL_INT_MAX

from faker import Faker
from random import randint

fake = Faker(locale="pt_BR")


def fake_user():
    user = Usuario()
    user.id = randint(0, SMALL_INT_MAX)
    user.nome = fake.name()
    user.email = fake.email()
    return user


def fake_device(user: Usuario):
    device = Dispositivo()
    device.id = randint(0, SMALL_INT_MAX)
    device.agente = fake.user_agent()
    device.endereco = fake.ipv4()
    device.ultima_atividade = fake.date_this_century()
    device.data_login = fake.date_this_century()
    device.token = fake.hexify("^" * 64)
    device.usuario_id = user.id
    return device
