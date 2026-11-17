"""Short explanations of every feast and fast key in feasts.py, shown when a feast or fast name is clicked.

One plain-text paragraph per key (two to four sentences): what is commemorated, the scriptural or traditional
basis, and one characteristic observance. Dates and lengths that differ between churches are stated in general
terms here; the tradition's own rule is added beneath the text by pages.py from feasts.py.
Written for this app (Nov 2026) from standard reference knowledge; not individually source-checked.
"""
from __future__ import annotations

TEXT: dict[str, str] = {
    # ------------------------------------------------------------------ Pascha and Holy Week
    "pascha": (
        "The Resurrection of Christ on the third day after the Crucifixion, the oldest and greatest Christian feast "
        "('Feast of Feasts'). Its name comes from the Hebrew Pesach, Passover. Since the Council of Nicaea (325) it is "
        "kept on the Sunday after the first full moon of spring, but Western and Eastern churches compute that date "
        "with different calendars and tables, so the two Easters often fall on different Sundays."),
    "fasika": (
        "Ethiopian and Eritrean Easter, the Resurrection of Christ. It ends the 55-day Great Fast (Abiy Tsom) with a "
        "night liturgy that closes in the early hours of Sunday, after which the fast is broken at home."),
    "palm_sunday": (
        "Christ's entry into Jerusalem a week before the Resurrection, greeted by crowds with palm branches and cries "
        "of 'Hosanna' (in all four Gospels). It opens Holy Week; palms, olive or willow branches are blessed and "
        "carried in procession."),
    "hosanna": (
        "Ethiopian Palm Sunday, Christ's entry into Jerusalem. Worshippers receive palm fronds, often tied into "
        "rings or small crosses and worn through the following days, and Holy Week (Himamat) begins."),
    "lazarus_saturday": (
        "The raising of Lazarus from the dead at Bethany (John 11), read as a pledge of the general resurrection. "
        "With Palm Sunday it forms the bridge between the forty days of Lent and Holy Week."),
    "holy_thursday": (
        "The Last Supper: Christ's institution of the Eucharist, his washing of the disciples' feet and his betrayal "
        "in Gethsemane. Many rites wash feet during the service; the Latin Church also blesses the holy oils, and in "
        "Kerala the day is Pesaha Thursday, marked with a special unleavened bread."),
    "covenant_thursday": (
        "The Coptic name for Holy Thursday: the Last Supper, at which Christ gave the 'new covenant' in his blood. The "
        "day's Liturgy of the Basin (Laqqan) re-enacts his washing of the disciples' feet."),
    "good_friday": (
        "The Crucifixion, death and burial of Christ, kept as the strictest fast day of the year. Byzantine churches "
        "carry the Epitaphios (an embroidered image of Christ in the tomb) in procession; the Latin Church holds the "
        "Celebration of the Passion with veneration of the Cross and no Mass."),
    "siklet": (
        "Ethiopian Good Friday, the Crucifixion. The faithful stand through a day-long service of readings and "
        "repeated prostrations (sigdet), and fast until the evening."),
    "holy_saturday": (
        "The day Christ lay in the tomb and, in Christian belief, descended to the dead to free them. Night ends with "
        "the Easter Vigil; in Jerusalem the Orthodox receive the Holy Fire from the Holy Sepulchre that afternoon."),
    "thomas_sunday": (
        "The Sunday after Pascha, recalling the apostle Thomas, who doubted until he touched the wounds of the risen "
        "Christ and confessed 'My Lord and my God' (John 20). Byzantine books also call it Antipascha."),
    "divine_mercy": (
        "The Second Sunday of Easter in the Catholic Church, named in 2000 by Pope John Paul II after the devotion to "
        "God's mercy promoted by the Polish nun St Faustina Kowalska (d. 1938)."),
    "mid_pentecost": (
        "The 25th day after Pascha, half-way to Pentecost, recalling Christ teaching in the Temple 'in the midst of "
        "the feast' (John 7) and offering living water. In Greek practice water is often blessed on this day."),
    "ascension": (
        "Christ's ascension into heaven forty days after the Resurrection, in the sight of the apostles on the Mount "
        "of Olives (Acts 1). It falls on a Thursday; some Latin dioceses move it to the following Sunday."),
    "pentecost": (
        "The descent of the Holy Spirit on the apostles fifty days after Pascha, when they began to preach in many "
        "languages (Acts 2); often called the birthday of the Church. Byzantine churches keep it as Trinity Day, "
        "with kneeling prayers at Vespers after fifty days without kneeling."),
    # ------------------------------------------------------------------ pre-Lent and Lent
    "zacchaeus_sunday": (
        "In Slavic and Antiochian usage, the Gospel of the tax collector Zacchaeus, who climbed a tree to see Christ "
        "and repented (Luke 19). It is the first signal that the Lenten season is approaching."),
    "publican_pharisee": (
        "The parable of the humble tax collector and the boastful Pharisee (Luke 18). It opens the Lenten Triodion "
        "and is followed by a week without fasting, to discourage pride in fasting."),
    "prodigal_son": (
        "The parable of the son who squandered his inheritance and was welcomed home (Luke 15): the second "
        "pre-Lenten Sunday, on repentance and the father's forgiveness."),
    "meatfare_sunday": (
        "The Sunday of the Last Judgment (Matthew 25), the last day on which meat is eaten before Pascha. The "
        "following week is 'cheese-fare': dairy, eggs and fish are still allowed."),
    "cheesefare_sunday": (
        "Forgiveness Sunday, recalling Adam's expulsion from Paradise; the last day for dairy and eggs. At Vespers "
        "clergy and people ask one another's forgiveness, and Great Lent begins the next day (Clean Monday)."),
    "ash_wednesday": (
        "The first day of Lent in the Latin Church. Ashes are marked on the forehead with the words 'Remember that "
        "you are dust', and it is a day of fasting and abstinence from meat."),
    "lent": (
        "The forty days of prayer, fasting and almsgiving before Easter in the Latin Church, recalling Christ's forty "
        "days in the desert. It runs from Ash Wednesday to the Mass of the Lord's Supper on Holy Thursday; Sundays "
        "are not fast days."),
    "great_lent": (
        "The forty-day fast before Holy Week and Pascha, recalling Christ's forty days in the desert. Traditionally "
        "meat, dairy, eggs, fish, wine and oil are given up on most days, with relaxations at weekends and on "
        "certain feasts; it is a season of long services and almsgiving."),
    "great_lent_coptic": (
        "The Coptic Great Fast of 55 days: a preparation week (by tradition linked to the emperor Heraclius), forty "
        "days recalling Christ's fast in the desert, and Holy Week (Pascha Week). It is kept without animal "
        "products, usually with abstinence from all food until the afternoon."),
    "abiy_tsom": (
        "The Ethiopian Great Fast (also Hudade), 55 days before Fasika: the week of Heraclius, forty days recalling "
        "Christ's fast, and Holy Week. Food is wholly vegan and traditionally not eaten until mid-afternoon on "
        "weekdays."),
    "great_lent_armenian": (
        "Medz Bahk, the Armenian Great Lent: forty days before Holy Week, beginning after the carnival-like Poon "
        "Barekendan. It is kept without meat, dairy and eggs, with Lenten hymns and the curtain of the altar "
        "drawn closed."),
    "sawma_rabba": (
        "The Great Fast of the Church of the East and the Chaldean and Syro-Malabar churches, beginning after "
        "Pethurta Sunday (the 'leave-taking' of food) seven weeks before Easter. In India it is called the "
        "fifty-days fast."),
    # ------------------------------------------------------------------ Nineveh / catechumens
    "nineveh_fast": (
        "Three days of repentance recalling Jonah's preaching to Nineveh and the city's fast (Jonah 3), kept two to "
        "three weeks before Great Lent by the Coptic, Syriac and East Syriac churches. In the Church of the East it "
        "is the Rogation of the Ninevites, associated with deliverance from a plague in the sixth century."),
    "tsome_nenewe": (
        "The Ethiopian Fast of Nineveh: three days (Monday to Wednesday) recalling the repentance of Nineveh after "
        "Jonah's preaching, two weeks before the Great Fast."),
    "jonah_feast": (
        "'Jonah's Pascha': the Coptic Church ends the Fast of Nineveh by celebrating Jonah's deliverance from the "
        "great fish after three days, which Christ himself made a sign of his Resurrection (Matthew 12:40)."),
    "catechumens_fast": (
        "Arajavorats, the first fast of the Armenian year: five days, three weeks before Great Lent, corresponding to "
        "the Nineveh fast of other Eastern churches. Armenian tradition links it to the fast before St Gregory the "
        "Illuminator baptised King Tiridates and his people."),
    # ------------------------------------------------------------------ Latin movable and seasonal feasts
    "trinity_sunday": (
        "The Sunday after Pentecost in the Latin Church, honouring the doctrine of the Trinity: one God in Father, "
        "Son and Holy Spirit. It was extended to the whole Western Church in 1334."),
    "corpus_christi": (
        "The feast of the Body and Blood of Christ, honouring his presence in the Eucharist, instituted in 1264 "
        "after the visions of St Juliana of Liège. Processions carry the consecrated Host through the streets; in "
        "many countries it is moved to the following Sunday."),
    "sacred_heart": (
        "A Latin solemnity honouring the love of Christ, symbolised by his heart, on the Friday after the second "
        "Sunday after Pentecost. It spread from the 17th-century visions of St Margaret Mary Alacoque and became "
        "universal in 1856."),
    "immaculate_heart": (
        "A memorial of the Virgin Mary's love for God and humanity, kept the day after the Sacred Heart. The "
        "devotion grew after the Fátima apparitions (1917) and was extended to the whole Latin Church in 1944."),
    "christ_the_king": (
        "The last Sunday of the Latin liturgical year, proclaiming Christ as ruler of all creation. Pius XI "
        "instituted it in 1925, amid rising secularism and nationalism."),
    "advent_1": (
        "The beginning of the Latin liturgical year and of Advent: four Sundays of preparation for Christmas and for "
        "Christ's second coming. Violet vestments are worn and a wreath of candles is often lit week by week."),
    "holy_family": (
        "The family of Jesus, Mary and Joseph, kept on the Sunday after Christmas (or 30 December) as a model for "
        "Christian family life. It became a feast of the whole Latin Church in 1921."),
    "baptism_of_the_lord": (
        "Christ's baptism by John in the Jordan, when the Spirit descended as a dove and the Father's voice was "
        "heard (Matthew 3). In the Latin Church it closes the Christmas season on the Sunday after Epiphany."),
    # ------------------------------------------------------------------ Nativity cycle
    "nativity": (
        "The birth of Jesus at Bethlehem (Matthew 1-2, Luke 2). Rome attests 25 December in 336; churches that "
        "follow the Julian calendar keep the same date, which now falls on 7 January civil, and the Coptic Church "
        "keeps it in the month of Koiak, also on 7 January civil."),
    "genna": (
        "Ethiopian Christmas, the birth of Christ, after the forty-day Fast of the Prophets. Many attend an all-night "
        "liturgy, pilgrims gather at Lalibela, and a field game also called genna is traditionally played."),
    "nativity_theophany": (
        "The Armenian Church keeps Christ's Nativity and his Baptism together on 6 January, the older Eastern "
        "practice from before 25 December spread. The day includes the Blessing of Water; the Armenian Patriarchate "
        "of Jerusalem keeps it by the Julian calendar (19 January civil)."),
    "nativity_fast": (
        "A fast of preparation for the Nativity of Christ, the Eastern counterpart of Advent. Its length varies: "
        "forty days in the Byzantine rite (Philip's Fast, from 15 November), forty-three in the Coptic Church, and "
        "shorter fasts in the Syriac churches."),
    "nativity_fast_armenian": (
        "The Armenian week of fasting immediately before the Nativity and Theophany of 6 January."),
    "tsome_nebiyat": (
        "The Ethiopian Fast of the Prophets, about forty days before Genna, recalling the prophets who foretold "
        "Christ's coming. Food is vegan and the fast ends with the Christmas liturgy."),
    "mary_mother_of_god": (
        "The octave day of Christmas in the Latin Church, honouring Mary as Mother of God (Theotokos), the title "
        "affirmed at the Council of Ephesus (431). It is also the World Day of Peace."),
    "circumcision": (
        "The circumcision and naming of Jesus on the eighth day after his birth (Luke 2:21). Byzantine churches keep "
        "St Basil the Great on the same day."),
    "epiphany": (
        "The manifestation of Christ to the nations, centred in the West on the visit of the Magi (Matthew 2), "
        "traditionally also recalling his baptism and the wedding at Cana. Kept on 6 January or the Sunday between "
        "2 and 8 January."),
    "theophany_eve": (
        "The eve of Theophany, a strict fast day in the Byzantine rite. The Great Blessing of Water is often "
        "served on this day as well as on the feast."),
    "theophany": (
        "The Baptism of Christ in the Jordan, when the Trinity was revealed: the Father's voice and the Spirit as a "
        "dove (Matthew 3). Water is solemnly blessed and in many places a cross is thrown into a river or the sea."),
    "ketera": (
        "The eve of Timkat in Ethiopia. The tabots (consecrated tablets representing the Ark of the Covenant) are "
        "carried in procession to a river or pool, where clergy and faithful keep vigil overnight; a fast day."),
    "timkat": (
        "Ethiopian Epiphany, the Baptism of Christ. After the night vigil the water is blessed and sprinkled on the "
        "crowds, and the tabots return to their churches in festive procession (UNESCO intangible heritage, 2019)."),
    "wedding_at_cana": (
        "Christ's first sign, changing water into wine at a wedding in Cana of Galilee (John 2). The Coptic Church "
        "keeps it two days after Theophany as one of the minor feasts of the Lord."),
    "presentation_of_the_lord": (
        "The presentation of the infant Jesus in the Temple forty days after his birth and the purification of "
        "Mary, when the aged Simeon and the prophetess Anna recognised him (Luke 2:22-40). Candles are blessed "
        "('Candlemas'); in Armenia bonfires are lit on its eve (Trndez)."),
    "meeting_of_the_lord": (
        "The Byzantine name for the Presentation: the 'meeting' (Hypapante) of the infant Christ with the elder "
        "Simeon in the Temple forty days after his birth, when Simeon sang 'Lord, now lettest thou thy servant "
        "depart in peace' (Luke 2)."),
    # ------------------------------------------------------------------ feasts of the Lord, Cross and saints
    "transfiguration": (
        "Christ shone with divine light on a mountain (traditionally Tabor) before Peter, James and John, with Moses "
        "and Elijah beside him (Matthew 17). Byzantine churches bless grapes and other first fruits."),
    "debre_tabor": (
        "Ethiopian feast of the Transfiguration on Mount Tabor. On its eve boys go from house to house singing and "
        "receive bread (buhe), and bonfires are lit."),
    "vardavar": (
        "The Armenian feast of the Transfiguration, fourteen weeks after Easter and one of the five tabernacle "
        "feasts. It is famous for the custom of drenching one another with water, inherited from a pre-Christian "
        "summer festival."),
    "vardavar_fast": (
        "The Armenian week of fasting (Monday to Friday) before Vardavar, the Transfiguration."),
    "exaltation_cross": (
        "The finding of the True Cross in Jerusalem by the Empress Helena (c. 326), the dedication of the Church of "
        "the Holy Sepulchre (335), and its recovery from the Persians by the emperor Heraclius (630). The Cross is "
        "raised and venerated, and Byzantine churches keep it as a fast day."),
    "exaltation_cross_armenian": (
        "Khachverats, the greatest Armenian feast of the Cross and one of the five tabernacle feasts, on the Sunday "
        "nearest 14 September. It recalls the Cross's finding by Helena and its return to Jerusalem by Heraclius."),
    "exaltation_fast_armenian": (
        "The Armenian week of fasting (Monday to Friday) before Khachverats, the Exaltation of the Cross."),
    "meskel": (
        "Ethiopian 'Finding of the True Cross'. Legend tells that the smoke of Empress Helena's bonfire showed where "
        "the Cross lay buried; on the eve a great bonfire (demera) is lit (UNESCO intangible heritage, 2013)."),
    "feast_of_the_cross": (
        "The Coptic three-day feast of the Cross (17-19 Thout), recalling the dedication of the Church of the "
        "Resurrection in Jerusalem built by the Empress Helena over the place of Christ's tomb."),
    "feast_of_the_cross_2": (
        "The Coptic commemoration of the Empress Helena's finding of the Cross of Christ in Jerusalem. It often "
        "falls within Great Lent, so it is kept more soberly than the September feast."),
    "entry_into_egypt": (
        "The flight of the Holy Family into Egypt to escape Herod (Matthew 2:13-15). Copts venerate many places the "
        "family is said to have stayed, among them Old Cairo and the monastery of al-Muharraq."),
    "nativity_john_baptist": (
        "The birth of John the Baptist to the aged Zechariah and Elizabeth (Luke 1), six months before Christmas. "
        "He is one of the very few saints whose birth, not death, is celebrated."),
    "beheading_john_baptist": (
        "The martyrdom of John the Baptist, beheaded by Herod Antipas at the request of Herodias's daughter "
        "(Mark 6). In the Byzantine rite it is a strict fast day."),
    "peter_paul": (
        "The apostles Peter and Paul, by tradition martyred in Rome under Nero in the 60s: Peter crucified and Paul "
        "beheaded. In the Byzantine rite the feast ends the Apostles' Fast."),
    "apostles_feast": (
        "The Coptic and Ethiopian feast of the martyrdom of Sts Peter and Paul, which ends the Apostles' Fast."),
    "apostles_fast": (
        "A fast after Pentecost before the feast of Sts Peter and Paul, recalling that the apostles fasted before "
        "setting out to preach. Its length depends on the date of Pascha: in the Byzantine rite it runs from the "
        "Monday after All Saints' Sunday to 28 June and may be very short or vanish."),
    "tsome_hawaryat": (
        "The Ethiopian Apostles' Fast, from the day after Pentecost until the feast of Sts Peter and Paul, "
        "recalling the apostles' fast before their mission."),
    "apostles_fast_syriac": (
        "The short Syriac fast before the feast of Sts Peter and Paul on 29 June."),
    "joseph": (
        "St Joseph, husband of the Virgin Mary and guardian of Jesus. Pius IX declared him patron of the universal "
        "Church in 1870."),
    "maron": (
        "St Maron (d. 410), a Syriac hermit near Cyrrhus in northern Syria. The monastic movement of his disciples "
        "gave its name to the Maronite Church, whose patron he is."),
    "all_saints": (
        "All the saints, known and unknown. The feast was fixed on 1 November in Rome in the 8th to 9th centuries."),
    "all_saints_sunday": (
        "The first Sunday after Pentecost in the Byzantine rite, honouring all the saints as the fruit of the Holy "
        "Spirit's descent. The Apostles' Fast begins the next day."),
    "all_souls": (
        "Prayer for all the faithful departed. The day spread through the Western Church from the abbey of Cluny "
        "around the year 1000; families visit and decorate graves."),
    "church_new_year": (
        "1 September, the Indiction: the start of the Byzantine church year, inherited from the Roman tax cycle. "
        "The Gospel tells of Christ reading Isaiah in the synagogue of Nazareth; since 1989 it is also a day of "
        "prayer for the environment."),
    "nayrouz": (
        "The Coptic New Year (1 Thout). Years are counted in the Era of the Martyrs, from 284, the accession of "
        "Diocletian, so the day also honours the martyrs; red dates and other red foods are traditional."),
    "enkutatash": (
        "The Ethiopian New Year (1 Meskerem), at the end of the rainy season, also the feast of St John the Baptist. "
        "The name ('gift of jewels') is linked to the Queen of Sheba's return from Solomon."),
    # ------------------------------------------------------------------ feasts of the Virgin Mary
    "annunciation": (
        "The archangel Gabriel's announcement to the Virgin Mary that she would conceive the Son of God, and her "
        "consent (Luke 1:26-38). It falls nine months before the Nativity, and even in Lent it is kept as a feast."),
    "nativity_theotokos": (
        "The birth of the Virgin Mary to Joachim and Anna, as told in the 2nd-century Protoevangelium of James. In "
        "the Byzantine year it is the first great feast after the new year of 1 September."),
    "conception_theotokos": (
        "The conception of the Virgin Mary by Saint Anna, kept by the Armenian Church on 9 December."),
    "immaculate_conception": (
        "The Catholic belief that Mary was preserved from original sin from the moment of her conception (not the "
        "virgin birth of Christ). Pius IX defined it as dogma in 1854."),
    "entry_theotokos": (
        "The presentation of the child Mary in the Temple at Jerusalem by her parents Joachim and Anna, where she "
        "was dedicated to God; the story comes from the Protoevangelium of James."),
    "protection_theotokos": (
        "Pokrov: the vision of St Andrew the Fool-for-Christ in the Blachernae church at Constantinople (10th "
        "century), in which the Mother of God spread her veil over the people in protection. It is especially "
        "loved in the Slavic churches and Romania."),
    "dormition": (
        "The 'falling asleep' of the Mother of God: her death in the presence of the apostles and, in tradition, her "
        "being taken bodily into heaven. It is the last great feast of the Byzantine year."),
    "dormition_fast": (
        "The two-week fast of 1-14 August before the Dormition of the Theotokos, kept as strictly as Great Lent "
        "except on the Transfiguration (6 August), when fish is allowed."),
    "assumption": (
        "The end of the Virgin Mary's earthly life and her being taken body and soul into heaven. For Catholics it "
        "has been dogma since 1950 (Pius XII); the Coptic and Syriac churches keep it after the Fast of the Virgin."),
    "assumption_armenian": (
        "The Armenian Assumption of the Holy Mother of God, on the Sunday nearest 15 August and one of the five "
        "tabernacle feasts. Grapes are blessed and eaten for the first time in the season."),
    "assumption_fast_armenian": (
        "The Armenian week of fasting (Monday to Friday) before the Assumption of the Holy Mother of God."),
    "filseta": (
        "Ethiopian feast of the Assumption of the Virgin Mary, which ends the two-week Filseta fast."),
    "tsome_filseta": (
        "The Ethiopian two-week fast before the feast of the Assumption, among the most widely kept fasts, observed "
        "even by children and with many attending church daily."),
    "virgin_fast": (
        "The Fast of the Virgin before her Assumption in August. In Egypt it is kept by the Coptic Church for two "
        "weeks and very widely observed by lay people; the Syriac Orthodox Church keeps five days."),
}

WEEKLY = (
    "Since the Didache (about 100 AD) Christians have fasted on Wednesdays, when Christ was betrayed, and on "
    "Fridays, the day of the Crucifixion. Eastern churches keep both days outside fast-free weeks; the Latin "
    "Church keeps Friday as a day of penance."
)


def text(key: str) -> str | None:
    return TEXT.get(key)
