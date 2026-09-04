# GardenIQ

Automação de mini jardim indoor com Raspberry Pi 3B: controle de irrigação
por malha fechada (sensor de umidade do solo + temperatura), ventilação e
dashboard web local com parâmetros ajustáveis em tempo real.

## Hardware

- Raspberry Pi 3B v1.2
- Sensor capacitivo de umidade do solo
- DS18B20 (temperatura da terra) e/ou DHT22 (temperatura/umidade do ar)
- Conversor ADC: MCP3008 (SPI)
- Cooler 5V (ventilação)
- Bomba d'água impressa em 3D (motor RC) acionada por relé/MOSTFET
- Reservatório posicionado abaixo do vaso, evitando efeito sifão

## Estrutura

```
jardim/
├── irrigacao.py         # loop de controle (le sensores, aciona rele/bomba)
├── dashboard.py          # servidor Flask (interface web)
├── config.json           # parametros atuais (cultura, limites, tempos)
├── presets.py            # presets de parametros por cultura
├── templates/
│   └── index.html        # interface do dashboard
└── systemd/
    ├── gardeniq-irrigacao.service
    └── gardeniq-dashboard.service
```

## Instalação

```bash
git clone <url-do-repo>
cd jardim
pip3 install flask spidev RPi.GPIO
```

Habilitar no `raspi-config` (Interface Options):
- SPI (para o MCP3008)
- 1-Wire (para o DS18B20)

## Uso manual

```bash
python3 irrigacao.py &
python3 dashboard.py
```

Acesse `http://<IP_DO_PI>:5000` de outro dispositivo na mesma rede.

## Rodando como serviço (systemd)

```bash
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now gardeniq-irrigacao.service
sudo systemctl enable --now gardeniq-dashboard.service
```

Verificar status e logs:

```bash
systemctl status gardeniq-irrigacao.service
journalctl -u gardeniq-irrigacao.service -f
```

**Importante:** ajuste `User` e `WorkingDirectory` nos arquivos `.service`
conforme o usuário e o caminho onde o repositório for clonado no seu Pi.

## Integração

O dashboard escreve os parâmetros em `config.json`. O `irrigacao.py` lê esse
arquivo a cada ciclo, então mudanças feitas pela interface web (cultura,
limites de umidade, temperatura, tempos) são aplicadas sem reiniciar o
serviço de controle.
