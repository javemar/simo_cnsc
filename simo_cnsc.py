from selenium  import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re
import pandas as pd

driver = webdriver.Chrome()
driver.get("https://simo.cnsc.gov.co/#ofertaEmpleo")


time.sleep(5)

elemento_departamento = driver.find_element_by_id("dijit_form_FilteringSelect_1")

elemento_departamento.clear()
elemento_departamento.send_keys(u"Bogotá, D.C.")
elemento_departamento.click()

boton_buscar = driver.find_element_by_id("dijit_form_Button_12_label")
boton_buscar.click()

time.sleep(2)
datos = {"titulo":[] , "descripciones":[]}


def find_links_pages(driver):
	links = driver.find_elements_by_class_name("dgrid-page-link")
	links_filtro = []
	for l in  links:
		try:
			l.text
			links_filtro.append(l.text)
		except Exception as e:
			pass

	links_numbers = [  int(l) for l in links_filtro if re.findall(r"^\d+$",  l)  ]

	return links, links_numbers

	
maximo_numero = max( find_links_pages(driver)[1])

for j in range(1,maximo_numero):
	print "procesando pagina {}".format(j)
	elementos  = driver.find_elements_by_class_name("dgrid-row")
	for e in elementos:
		
		interior = e.find_elements_by_class_name("itemEmpleo")
		if len(interior)>0:
			interior[0].click()
			datos["titulo"].append(interior[0].text)
			datos["descripciones"].append(e.find_element_by_class_name("detalleEmpleo").text)
			
			
	links  = find_links_pages(driver)[0]
	
	for l in links:
		try:
			texto_link = l.text
			if str(j+1)  == texto_link:
				l.click()
				time.sleep(1)
		except Exception as e:
			pass

df = pd.DataFrame(datos)

df["nivel_empleo_2"] =  df.titulo.str.extract(r"(?P<nivel_empleo>^.+?)(?=\n)")
df["nivel_empleo"] =  df.titulo.str.extract(r"(?<=Nivel: )(.+?)(?=Denomina)")
df["denominacion"] = df.titulo.str.extract(r"(?<=Denominaci.n: )(.+?)(?=Grado)")
df["grado"] = df.titulo.str.extract(r"(?<=Grado: )(.+?)(?=C.digo)")
df["codigo"] =  df.titulo.str.extract(r"(?<=C.digo: )(.+?)(?=N.mero)")
df["numero_opec"] = df.titulo.str.extract(r"(?<=OPEC: )(.+?)(?=Asignaci.n)")
df["salario"] =  df.titulo.str.extract("(?<=Salarial:\s\$\s)(?P<hola>\d+)").astype(float)
df["lugar"] = df.titulo.str.extract(r"(?P<lugar>\d+\n.+?)(?=Cierre de)").lugar.str.replace(r"\d+?\n", "")
df["cierre_inscripciones"] = df.titulo.str.extract(r"(?<=inscripciones: )(.+?)(?=\nN)")
df["numero_vacantes"] = df.titulo.str.extract(r"(?<=vacantes: )(.+)")

df["proposito"] = df.descripciones.str.extract(r"(?<=prop.sito\n)(?P<resultado>.+)")
df["funciones"] = df.descripciones.str.replace(r"\n", "").str.extract(r"(?<=funciones)(?P<resultado>.+)(?=requisitos)")
df["estudios"] = df.descripciones.str.extract(r"(?<=Estudio: )(?P<resultado>.+)")
df["experiencia"] = df.descripciones.str.extract(r"(?<=Experiencia: )(?P<resultado>.+)")
df["experiencia_numerica"] = df.experiencia.str.replace(r"[^\d]", "")
df["dependencia"] = df.descripciones.str.extract(r"(?<=Dependencia: )(?P<resultado>.+)(?=Muni)")
df["Municipio"] = df.descripciones.str.extract(r"(?<=Municipio: )(?P<resultado>.+)(?=Cantidad)")
df["numero_vacantes_2"] = df.descripciones.str.extract(r"(?<=Cantidad: )(?P<resultado>.+)")


df.to_excel(r"/home/javemar/Documents/Javier/pythonscripts/simo_cnsc/df.xlsx", index=False)
