terrain = ("no ground", "water", "mountain", "plain", "stone")

characters = {}
locations = {}


class Room:
    def __init__(self, d):
        self.number = d["number"]
        self.name = d["name"]
        self.description = d["description"]
        self.indoors = d["indoors"]
        self.terrain = d["terrain"]
        self.exits = d["exits"]
        self.objects = d["objects"]

    def _exits(self):
        output = "&gExits:&N"
        if len(self.exits) == 0:
            output += " &RNone!&N"
        else:
            count = 0
            for exit in self.exits:
                if count > 0:
                    output += "&C -&N"
                output += f"&c {exit['direction'].title()}&N"
                count += 1
        return output + "\n&N"

    def _objects(self):
        output = ""
        if len(self.objects) > 0:
            for obj in self.objects:
                output += f"{obj.room_description}\n"
        return output

    @property
    def characters(self):
        char = []
        for c, r in locations.items():
            if r == self.number:
                char.append(c)
        return char

    def _characters(self):
        output = ""
        if len(self.characters) > 0:
            for character in self.characters:
                output += f"{characters[character].name.title()} stands here\n"
        return output

    def __str__(self):
        output = f"{self.name}\n     {self.description}\n"
        output += self._exits()
        output += self._objects()
        output += self._characters()
        return output
