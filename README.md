# AgendaBot

Agendabot is a discord bot created to help university students better schedule their academic deadlines while also helping with planning casual events to relieve stress and socialize during the online terms. This bot was created by Max Ning, Lukas Boelling and Jordan Jamali during the 2020 online Oxford Hackathon.

## Command List
*`$help` : provides a list of commands available in a specific discord channel
**For Deadlines** \
*`$new deadline [course_code], [deadline_name], [due_date]` : adds a new deadline to the deadlines database based on the parameters shown (commas are necessary)\
*`$remove deadline [index]` : deletes a deadline from the deadlines database through an index \
*`$clear deadlines` : clears all deadlines from the deadline database. Should be used very cautiously. \
*`$list deadlines` : list the deadlines with their indices (index is used for deletion) \
**For Events** \
*`$new event [event_name], [description], [start_date]` : adds a new event to the events database based on the parameters shown (commas are necessary)\
*`$remove event [index]` : deletes a event from the events database through an index \
*`$clear events` : clears all events from the events database. Should be used very cautiously. \
*`$list events` : list all upcoming with their indices (index is used for deletion)



