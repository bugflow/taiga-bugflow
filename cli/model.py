

class KanbanActivity:
    # This is hard-coded against the hand-rolled query.
    # Deal with it.
    def __init__(self, row):
        self.raw = row

    @property
    def transition(self):
        return str(self.raw[0])

    @property
    def from_state(self):
        return self.raw[0][0]

    @property
    def to_state(self):
        return self.raw[0][1]

    @property
    def transition_name(self):
        return self.raw[1]

    @property
    def ticket_id(self):
        return self.raw[2]

    @property
    def ticket_name(self):
        return self.raw[3]

    @property
    def transition_time(self):
        return self.raw[4]

    @property
    def story_points(self):
        return self.raw[5]

    def __str__(self):
        if not self.story_points:
            p = '-'
        else:
            p = "%s points" % self.story_points
        return "%s [%s] [%s] (%s --> %s) [%s] %s" % (
            self.transition_time,
            self.ticket_id,
            p,
            self.from_state,
            self.to_state,
            self.transition_name,
            self.ticket_name
        )
