# Google Calendar URLs

There does not seem to be any actual documentation on how to craft a Google Calendar URL with specific values. This seems to work for this application.

```text
https://calendar.google.com/calendar/render?
action=TEMPLATE
text=Person and Person 1-on-1
add=email@example.com,email2@example.com
details=description
```

## References

- https://dylanbeattie.net/2021/01/12/adding-events-to-google-calendar-via-a-link.html
- https://stackoverflow.com/questions/22757908/what-parameters-are-required-to-create-an-add-to-google-calendar-link
- https://github.com/InteractionDesignFoundation/add-event-to-calendar-docs/blob/main/services/google.md
