require(treemap)
require(DT)
require(circlize)
require(stringr)
require(hrbrthemes)
require(igraph)
require(gridExtra)
require(purrr)
require(dplyr)
require(plyr)
require(data.table)
require(jsonlite)
require(reshape2)
require(ggplot2)
require(ggrepel)
require(cowplot)
require(tidyr)
require(knitr)
require(kableExtra)
require(corpus)
require(wordcloud)
require(tm)
require(quanteda)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

allEps <- read.csv("./Archive//all_Episodes.csv",sep="\t")[,c(2:9)]
allEps$Series_Episode <- paste("S",allEps$SeriesNo,"E",allEps$EpisodeNo,sep="")
allEps$Index <- as.numeric(rownames(allEps))

#Fix major typos that present major problems later on
allEps[allEps$Character=="",]$Character <- "UNKNOWN"

allEps[allEps$SeriesNo==3 & allEps$EpisodeNo>1,]$EpisodeNo <- allEps[allEps$SeriesNo==3 & allEps$EpisodeNo>1,]$EpisodeNo + 1
allEps[allEps$EpisodeURL=="http://www.chakoteya.net/DoctorWho/3-1-5.htm",]$EpisodeNo <- 2


#Disambiguation of characters aided by users of the r/DoctorWHo subreddit. Particular thanks to reddit.com/user/HiFiThePanda

allEps[allEps$Character=="BARRAS",]$Character <- "BARRASS"
allEps[allEps$Character=="REDKANG",]$Character <- "REDKANGS"
allEps[allEps$Character=="GUARD-MASTERS",]$Character <- "GUARD-MASTER"
allEps[allEps$Character=="OPERATIVE-MASTERS",]$Character <- "OPERATIVE-MASTER"
allEps[allEps$Character=="ALLDALEKS",]$Character <- "DALEK"
allEps[allEps$Character=="BLACK" & !(allEps$Series_Episode %in% c("S15E5","S31E10")),]$Character <- "BLACKDALEK"

allEps[allEps$Character=="ANNE" & allEps$Series_Episode %in% c("S5E5"),]$Character <- "ANNETRAVERS"

allEps[allEps$Character=="TRAVERS" & allEps$Series_Episode %in% c("S5E5","S5E2"),]$Character <- "PROFTRAVERS"
allEps[allEps$Character=="TRAVERS" & allEps$Series_Episode %in% c("S23E3"),]$Character <- "CAPTTRAVERS"

allEps[allEps$Character=="JACKSON" & allEps$Series_Episode %in% c("S15E5"),]$Character <- "CMNDRJACKSON"
allEps[allEps$Character=="JACKSON" & allEps$Series_Episode %in% c("S20E5"),]$Character <- "SAILRJACKSON"

allEps[allEps$Character=="WILLIAMS" & allEps$Series_Episode %in% c("S7E4"),]$Character <- "PETRAWILLIAMS"

allEps[allEps$Character=="TYLER" & allEps$Series_Episode %in% c("S10E1"),]$Character <- "DRTYLER"

unique(allEps[allEps$Character=="SARAH",c(1,9)])

allEps[allEps$Character=="SARAH" & allEps$Series_Episode %in% c("S30E18"),]$Character <- "SARAH1"
allEps[allEps$Character=="SARAH" & allEps$Series_Episode %in% c("S39E7"),]$Character <- "SARAH2"

allEps[allEps$Character=="RUTH" & allEps$Series_Episode %in% c("S11E2"),]$Character <- "RUTH_ONE"
allEps[allEps$Character=="RUTH" & allEps$Series_Episode %in% c("S23E3"),]$Character <- "RUTHBAXTER"
allEps[allEps$Character=="RUTH" & allEps$Series_Episode %in% c("S9E5"),]$Character <- "RUTHINGRAM"
allEps[allEps$Character=="RUTH" & allEps$Series_Episode %in% c("S4E9"),]$Character <- "RUTHMAXTIBLE"
allEps[allEps$Character=="RUTH" & allEps$Series_Episode %in% c("S38E5","S38E10"),]$Character <- "RUTH"

allEps[allEps$Character=="ANGRSTROM",]$Character <- "ANGSTROM"

allEps[allEps$Character=="ASHILDR",]$Character <- "ASHILDIR"
allEps[allEps$Character=="ASHILDIR",]$Character <- "ASHILDIR"
allEps[allEps$Character=="ASHLIDR",]$Character <- "ASHILDR"

allEps[allEps$Character=="ABBOTT" & allEps$Series_Episode %in% c("S14E2"),]$Character <- "ABBOTT_ONE"
allEps[allEps$Character=="ABBOTT" & allEps$Series_Episode %in% c("S33E7"),]$Character <- "ABBOTT_TWO"

allEps[allEps$Character=="ADAM" & allEps$Series_Episode %in% c("S11E2"),]$Character <- "ADAM_ONE"
allEps[allEps$Character=="ADAM" & allEps$Series_Episode %in% c("S27E6","S27E7"),]$Character <- "ADAM_TWO"

allEps[allEps$Character=="ADELAIDE" & allEps$Series_Episode %in% c("S15E1"),]$Character <- "ADELAIDE_ONE"
allEps[allEps$Character=="ADELAIDE" & allEps$Series_Episode %in% c("S30E16","S27E7"),]$Character <- "ADELAIDE_TWO"

allEps[allEps$Character=="AMELIA" & allEps$Series_Episode %in% c("S13E6"),]$Character <- "AMELIARUMFORD"
allEps[allEps$Character=="AMELIA" & allEps$Series_Episode %in% c("S31E1","S31E13","S32E8"),]$Character <- "AMY"

allEps[allEps$Character=="ALPHA" & allEps$Series_Episode %in% c("S4E9"),]$Character <- "DALEK"
allEps[allEps$Character=="ALPHA" & allEps$Series_Episode %in% c("S9E2","S11E4"),]$Character <- "ALPHACENTAURI"

allEps[allEps$Character=="ANDREWS" & allEps$Series_Episode %in% c("S10E2"),]$Character <- "LTANDREWS"
allEps[allEps$Character=="ANDREWS" & allEps$Series_Episode %in% c("S19E7","S11E4"),]$Character <- "ANDREWS"

allEps[allEps$Character=="ANITA" & allEps$Series_Episode %in% c("S22E4"),]$Character <- "ANITA_ONE"
allEps[allEps$Character=="ANITA" & allEps$Series_Episode %in% c("S30E8","S30E9"),]$Character <- "ANITA_TWO"
allEps[allEps$Character=="ANITA" & allEps$Series_Episode %in% c("S32E8"),]$Character <- "ANITA_THREE"
allEps[allEps$Character=="ANITA" & allEps$Series_Episode %in% c("S38E7"),]$Character <- "ANITA_FOUR"

allEps[allEps$Character=="ANN" & allEps$Series_Episode %in% c("S4E8"),]$Character <- "ANNDAVIDSON"
allEps[allEps$Character=="ANN" & allEps$Series_Episode %in% c("S19E5"),]$Character <- "ANNTALBOT"

allEps[allEps$Character=="ARAK" & allEps$Series_Episode %in% c("S11E5"),]$Character <- "ARAK_ONE"
allEps[allEps$Character=="ARAK" & allEps$Series_Episode %in% c("S22E2"),]$Character <- "ARAK_TWO"

allEps[allEps$Character=="ASTRID" & allEps$Series_Episode %in% c("S5E4"),]$Character <- "ASTRIDFERRIER"
allEps[allEps$Character=="ASTRID" & allEps$Series_Episode %in% c("S30E0"),]$Character <- "ASTRID"

allEps[allEps$Character=="HARRIS" & allEps$Series_Episode %in% c("S5E6"),]$Character <- "HARRIS_ONE"
allEps[allEps$Character=="HARRIS" & allEps$Series_Episode %in% c("S30E4","S30E5","S30E11"),]$Character <- "HARRIS"

allEps[allEps$Character=="JONES" & allEps$Series_Episode %in% c("S5E6"),]$Character <- "MEGANJONES"
allEps[allEps$Character=="JONES" & allEps$Series_Episode %in% c("S10E5"),]$Character <- "PROFJONES"

allEps[allEps$Character=="MARSHAL" & allEps$Series_Episode %in% c("S9E4"),]$Character <- "MARSHAL_OF_SOLOS"
allEps[allEps$Character=="MARSHAL" & allEps$Series_Episode %in% c("S12E3"),]$Character <- "SONTARAN"
allEps[allEps$Character=="MARSHAL" & allEps$Series_Episode %in% c("S16E6"),]$Character <- "MARSHAL_OF_ATRIOS"

allEps[allEps$Character=="BILL" & allEps$Series_Episode %in% c("S8E2"),]$Character <- "BILLMINOR"
allEps[allEps$Character=="BILL" & allEps$Series_Episode %in% c("S22E1"),]$Character <- "GANGBILL"

allEps[allEps$Character=="MONK" & allEps$Series_Episode %in% c("S2E9","S3E3","S5E2"),]$Character <- "THEMONK"
allEps[allEps$Character=="MONK" & allEps$Series_Episode %in% c("S14E1"),]$Character <- "MONK"

allEps[allEps$Character=="BENNETT" & allEps$Series_Episode %in% c("S2E3"),]$Character <- "BENNETT_ONE"
allEps[allEps$Character=="BENNETT" & allEps$Series_Episode %in% c("S5E7"),]$Character <- "BENNETT_TWO"

allEps[allEps$Character=="JO" & allEps$Series_Episode %in% c("S30E4"),]$Character <- "JO_TWO"
allEps[allEps$Character=="JO" & allEps$Series_Episode %in% c("S33E11"),]$Character <- "JO_THREE"

allEps[allEps$Character=="DUGGAN" & allEps$Series_Episode %in% c("S5E7"),]$Character <- "DUGGAN_ONE"
allEps[allEps$Character=="DUGGAN" & allEps$Series_Episode %in% c("S17E2"),]$Character <- "DUGGAN_TWO"

allEps[allEps$Character=="OSGOOD" & allEps$Series_Episode %in% c("S6E5"),]$Character <- "OSGOOD_ONE"
allEps[allEps$Character=="OSGOOD" & allEps$Series_Episode %in% c("S8E5"),]$Character <- "OSGOOD_ONE"

allEps[allEps$Character=="YATES" & allEps$Series_Episode %in% c("S20E7"),]$Character <- "YATES_ONE"

allEps[allEps$Character=="BARCLAY" & allEps$Series_Episode %in% c("S4E2"),]$Character <- "BARCLAY_ONE"
allEps[allEps$Character=="BARCLAY" & allEps$Series_Episode %in% c("S9E3"),]$Character <- "BARCLAY_TWO"
allEps[allEps$Character=="BARCLAY" & allEps$Series_Episode %in% c("S30E15"),]$Character <- "BARCLAY_THREE"

allEps[allEps$Character=="MARY" & allEps$Series_Episode %in% c("S5E4"),]$Character <- "MARY_ONE"
allEps[allEps$Character=="MARY" & allEps$Series_Episode %in% c("S8E4"),]$Character <- "MARY_ONE"

allEps[allEps$Character=="RYAN" & allEps$Series_Episode %in% c("S5E7"),]$Character <- "RYAN_ONE"
allEps[allEps$Character=="GRAHAM" & allEps$Series_Episode %in% c("S34E12"),]$Character <- "GRAHAM_ONE"
allEps[allEps$Character=="DAN" & allEps$Series_Episode %in% c("S37E7"),]$Character <- "DAN_ONE"

allEps[allEps$Character=="GRAHAM-AND-YAZ-AND-RYAN" & allEps$Series_Episode %in% c("S37E4"),]$Character <- "GRAHAM-AND-YASMIN-AND-RYAN"

allEps[allEps$Character=="MARTHA" & allEps$Series_Episode %in% c("S15E3"),]$Character <- "MARTHA_ONE"
allEps[allEps$Character=="MARTHA" & allEps$Series_Episode %in% c("S16E3"),]$Character <- "MARTHA_TWO"

allEps[allEps$Character=="JACK" & allEps$Series_Episode %in% c("S22E3"),]$Character <- "JACK_ONE"
allEps[allEps$Character=="JACK" & allEps$Series_Episode %in% c("S27E9"),]$Character <- "JACK_TWO"

allEps[allEps$Character=="KATE" & allEps$Series_Episode %in% c("S3E7"),]$Character <- "KATE_ONE"

allEps[allEps$Character=="BEN" & allEps$Series_Episode %in% c("S15E1"),]$Character <- "BEN_ONE"
allEps[allEps$Character=="BEN" & allEps$Series_Episode %in% c("S29E10"),]$Character <- "BEN_TWO"
allEps[allEps$Character=="BEN" & allEps$Series_Episode %in% c("S32E0"),]$Character <- "BEN_THREE"

allEps[allEps$Character=="POLLY" & allEps$Series_Episode %in% c("S37E11"),]$Character <- "POLLY_ONE"

unique(allEps[allEps$Character=="QUINN",c(1,9,6)])

#Delete pilot episode
allEps <- allEps[allEps$Series_Episode != "S1E0",]
allEps <- allEps[allEps$Series_Episode != "S17E6",]

write.csv("all_Episodes.csv",sep="\t",x=allEps)