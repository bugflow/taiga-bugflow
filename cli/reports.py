class Kanban:
    def __init__(self, data):
        self._data = data  # bad to be implicit :(
        # FIXME: the repo object should return a domain object
        self._transitions = None  # good to be lazy

    def transition_names(self):
        if self._transitions:
            return self._transitions.keys()
        self._populate_transitions()
        return self._transitions.keys()

    def _populate_transitions(self):
        self._transitions = {}
        for r in self._data:
            if r.transition_name not in self._transitions.keys():
                self._transitions[r.transition_name] = []
            self._transitions[r.transition_name].append(r)

    def summary_table(self):
        table = []
        for t in self.transition_names():
            count = len(self._transitions[t])
            sp_missing = 0
            size = 0
            for r in self._transitions[t]:
                if r.story_points:
                    size += r.story_points
                else:
                    sp_missing += 1
            table.append(
                {
                    "transition": t,
                    "count": count,
                    "unsized": sp_missing,
                    "story_points": size
                }
            )
        return table
