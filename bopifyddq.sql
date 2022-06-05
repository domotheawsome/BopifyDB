/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


DROP TABLE IF EXISTS `Songs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;

/*creating the songs table */
CREATE TABLE Songs (
  /* song specific attributes */
  song_ID INT AUTO_INCREMENT,
  song_name VARCHAR(255) NOT NULL,
  song_genre VARCHAR(255) NOT NULL,

  /*making columns to later hold the foreign keys
  Can't make them foreign keys right now because the other tables haven't been created yet */
  artist_ID INT,
  album_ID INT,

  /* set primary key */
  PRIMARY KEY (song_ID)
)ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `Albums`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;

/* creating the albums table */
CREATE TABLE Albums (
  /* album specific attributes */
  album_ID INT AUTO_INCREMENT,
  album_name VARCHAR(255) NOT NULL,
  album_genre VARCHAR(255) NOT NULL,
  /*foreign key column*/
  artist_ID INT,
  PRIMARY KEY (album_ID)
)ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `Artists`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;

/* create the artists table  */
CREATE TABLE Artists (
  /* artist specific attributes */
  artist_ID INT AUTO_INCREMENT,
  artist_fname VARCHAR(255) NOT NULL,
  artist_lname VARCHAR(255) NULL,
  PRIMARY KEY (artist_ID)
)ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

/* need to alter the other tables to reflect the foreign keys
--you will notice that this is the same syntax from lines 46-53, just in the "alter table" setting */
ALTER TABLE Songs
  ADD CONSTRAINT fk_sng_1
  FOREIGN KEY (album_ID)
  REFERENCES Albums(album_ID)
  ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE Songs
  ADD CONSTRAINT fk_sng_2
  FOREIGN KEY (artist_ID)
  REFERENCES Artists(artist_ID)
  ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE Albums
  ADD CONSTRAINT fk_albm_1
  FOREIGN KEY (artist_ID)
  REFERENCES Artists(artist_ID)
  ON DELETE CASCADE ON UPDATE CASCADE;

  DROP TABLE IF EXISTS `Users`;
  /*!40101 SET @saved_cs_client     = @@character_set_client */;
  /*!40101 SET character_set_client = utf8 */;

/* same thing as when creating the songs/albums/artists thing */
  CREATE TABLE Users (
    user_ID INT AUTO_INCREMENT,
    user_name VARCHAR(255) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    PRIMARY KEY (user_ID)
  )ENGINE=InnoDB DEFAULT CHARSET=latin1;
  /*!40101 SET character_set_client = @saved_cs_client */;

  DROP TABLE IF EXISTS `Playlists`;
  /*!40101 SET @saved_cs_client     = @@character_set_client */;
  /*!40101 SET character_set_client = utf8 */;
  CREATE TABLE Playlists (
    playlist_ID INT AUTO_INCREMENT,
    playlist_name VARCHAR(255) NOT NULL,
    user_ID INT,
    PRIMARY KEY (playlist_ID),
    CONSTRAINT fk_ply1 FOREIGN KEY (user_ID)
    REFERENCES Users(user_ID)
  ON DELETE CASCADE ON UPDATE CASCADE
  )ENGINE=InnoDB DEFAULT CHARSET=latin1;
  /*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `PlaylistsInSong`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE PlaylistsInSong (
  playlistinsong_ID INT AUTO_INCREMENT,
  song_ID INT,
  playlist_ID INT,
  PRIMARY KEY (playlistinsong_ID),
  CONSTRAINT fk_ps1 FOREIGN KEY (song_ID)
  REFERENCES Songs(song_ID)
  ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_ps2 FOREIGN KEY (playlist_ID)
  REFERENCES Playlists(playlist_ID)
  ON DELETE CASCADE ON UPDATE CASCADE
)ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
