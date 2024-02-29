package main

import (
    "database/sql"
    "fmt"
    "log"
    "net/http"
    "time"

    _ "github.com/mattn/go-sqlite3"
    "github.com/nlopes/slack"
    "github.com/PuerkitoBio/goquery"
)

type Circular struct {
    Title string
    Link  string
    Date  string
}

func main() {
    // Create a connection to the database
    db, err := sql.Open("sqlite3", "./circulars.db")
    if err != nil {
        log.Fatal(err)
        return
    }
    
    // Create a table to store circulars
    _, err = db.Exec(`
        CREATE TABLE IF NOT EXISTS circulars (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            TITLE TEXT NOT NULL,
            LINK TEXT NOT NULL,
            DATE TEXT NOT NULL
        )
     `)
     if err != nil {
         log.Fatal(err)
         return
     }

     api := slack.New("<SLACK_TOKEN>")
     channelID := "<SLACK_CHANNEL_ID>"
     url := "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListingAll=yes&sid=1&ssid=0&smid=0"

     var lastCircular *Circular

     for {
         resp, err := http.Get(url)
         if err != nil {
             log.Fatal(err)
             return
         }
         defer resp.Body.Close()

         doc, err := goquery.NewDocumentFromReader(resp.Body)
         if err != nil {
             log.Fatal(err)
             return
         }

         var newCircular *Circular

         doc.Find("tr").Each(func(i int, s *goquery.Selection) {
             cells := s.Find("td")
             if cells.Length() == 3 {
                 newDate := cells.Eq(0).Text()
                 newCircularType := cells.Eq(1).Text()
                 titleLink := cells.Eq(2).Find("a")
                 newTitle := titleLink.Text()
                 newLink, _ := titleLink.Attr("href")

                 // Check if there's a new circular and update the database if necessary
                 if lastCircular == nil || newTitle != lastCircular.Title {
                     rowInDb := db.QueryRow("SELECT * FROM circulars WHERE TITLE=?", newTitle)

                     var id int
                     var title string
                     var link string
                     var date string

                     switch err = rowInDb.Scan(&id, &title, &link, &date); err {
                     case sql.ErrNoRows:
                         // Insert new record into database
                         _, err = db.Exec("INSERT INTO circulars (TITLE, LINK, DATE) VALUES (?, ?, ?)", newTitle, newLink, newDate)
                         if err != nil {
                             log.Fatal(err)
                             return
                         }
                         fmt.Println("New record inserted into database.")

                         // Send message to Slack channel
                         message := fmt.Sprintf("*New SEBI Circular*\n\nType: %s\n\nDate: %s\n\nTitle: %s\n\nLink: %s", newCircularType, newDate, newTitle, newLink)
                         _, _, err = api.PostMessage(channelID, slack.MsgOptionText(message, false))
                         if err != nil {
                             log.Fatal(err)
                             return
                         }

                         lastCircular = &Circular{newTitle, newLink, newDate}
                     case nil:
                        fmt.Println("Record already exists in database.")
                        return
                    default:
                        log.Fatal(err)
                        return
                    }
                }
            })

            // Sleep for 1 hour before checking again
            time.Sleep(time.Hour * 1)
        }

        // Close connection to the database
        db.Close()
}