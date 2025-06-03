import requests
import csv

capitais_ceps = {
    "Rio Branco": "69900-973",
    "Maceió": "57051-000",
    "Manaus": "69010-001",
    "Macapá": "68900-110",
    "Salvador": "40020-000",
    "Fortaleza": "60025-061",
    "Brasília": "70040-010",
    "Vitória": "29010-001",
    "Goiânia": "74005-010",
    "São Luís": "65010-440",
    "Belo Horizonte": "30130-003",
    "Campo Grande": "79002-330",
    "Cuiabá": "78005-100",
    "Belém": "66017-000",
    "João Pessoa": "58013-000",
    "Recife": "50010-240",
    "Teresina": "64000-060",
    "Curitiba": "80020-310",
    "Rio de Janeiro": "20011-000",
    "Natal": "59025-002",
    "Porto Velho": "76801-048",
    "Boa Vista": "69301-000",
    "Porto Alegre": "90020-021",
    "Florianópolis": "88010-001",
    "Aracaju": "49010-020",
    "São Paulo": "01001-000",
    "Palmas": "77001-090"
}



url = "https://abree.org.br/pagina/pontos/filtrar_listagem"  # Substitua pela URL correta

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

# Lista para armazenar todos os pontos
todos_os_pontos = []

for cidade, cep in capitais_ceps.items():
    payload = {
        "cep": cep,
        "distancia": 30999,
        "id_produto": 98
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        pontos = data.get("pontos", [])
        print(f"✅ {cidade}: {len(pontos)} pontos encontrados.")

        for ponto in pontos:
            ponto["cidade_consulta"] = cidade
            ponto["cep_consulta"] = cep
            todos_os_pontos.append(ponto)

    except Exception as e:
        print(f"❌ Erro ao buscar dados para {cidade}: {e}")

# Define os campos que queremos exportar
campos_csv = [
    "id", "numero", "nome", "endereco", "projeto", "canal", "porte", 
    "observacao", "domicilio", "status", "insert_data", "update_data",
    "lat", "lng", "porte_especial", "cidade_consulta", "cep_consulta"
]

# Salva em CSV
with open("pontos_de_coleta_capitais_notebook.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=campos_csv)
    writer.writeheader()
    writer.writerows(todos_os_pontos)

print("📁 Arquivo 'pontos_de_coleta.csv' salvo com sucesso.")
