# Keskustelualusta-X.0
Tsoha-projekti

# Aiheena on tehdä perinteinen keskustelusovellus.

Keskustelusovelluksessa voit:
- Luoda käyttäjän ylläpito-oikeuksilla tai ilman.
- Luoda viestiketjuja sekä poistaa omia viestiketjujaan.
- Voi kirjoittaa viestejä
- Hakea viestejä sekä viestiketjuja  tietyllä sanalla
- Lisätä tai poistaa foorumeita, jos on valinnut ylläpito-oikeudet.
- Tehdä salasia foorumeita ja määrittää ketkä voivat nähdä sen, jos on valinnut ylläpito-oikeudet.

Jatkokehiteltävää:
- UI hienommaksi
- Viestin alapuolella näkyvä aika, jolloin viesti on kirjoitettu voisi muokata.
- Laittaa viestiketjuihin tieto kuinka monta viestiä sen alle on kirjoitettu.


Sovelluksen testaaminen:
Sovellus ei ole testattavissa Fly.io:ssa, ohjeet kuin käynnistää sovellus paikallisesti:

- Kloonaa tämä repositorio omalle koneellesi ja siirry sen juurikansioon. Luo kansioon .env-tiedosto ja määritä sen sisältö seuraavanlaiseksi:
  ```
  DATABASE_URL=<tietokannan-paikallinen-osoite>
  SECRET_KEY=<salainen-avain>
  ```

- Aktivoi virtuaaliympäristö ja asenna sovelluksen riippuvuudet seuraavilla komennoilla:
  ```
  $ pyhton3 -m venv venv
  $ source venv/bin/activate
  $ pip install -r ./requirements.txt
  ```

- Määritä tietokannan skeema seuraavalla komennolla:
  ```
  $ psql < schema.sql
  ```

- Käynnistä sovellus:
  ```
  $ flask run
  ```