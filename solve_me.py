from http.server import BaseHTTPRequestHandler, HTTPServer


class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            self.completed_items = file.readlines()
            file.close()
        except Exception:
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def add(self, args):
        new_priority = int(args[0])
        for priority in self.current_items:
            if new_priority == priority:
                while new_priority + 1 in self.current_items:
                    new_priority += 1
                while new_priority + 1 > int(args[0]):
                    self.current_items[new_priority + 1] = self.current_items[new_priority]
                    new_priority -= 1
                break

        self.current_items[int(args[0])] = " ".join(args[1:])
        self.write_current()
        return (True, f'Added task: "{" ".join(args[1:])}" with priority {args[0]}')

    def done(self, args):
        if int(args[0]) in self.current_items:
            self.completed_items.append(self.current_items[int(args[0])])
            del self.current_items[int(args[0])]
            self.write_current()
            self.write_completed()
            return (True, f"Marked item as done.")
        else:
            return (False, f"Error: no incomplete item with priority {args[0]} exists.")

    def delete(self, args):
        if int(args[0]) in self.current_items:
            del self.current_items[int(args[0])]
            self.write_current()
            return (True, f"Deleted item with priority {args[0]}")
        else:
            return (False, f"Error: item with priority {args[0]} does not exist. Nothing deleted.")

    def ls(self):
        pending_tasks = ""
        for index, priority in enumerate(self.current_items):
            pending_tasks += f"{index + 1}. {self.current_items[priority]} [{priority}]\n"
        return (True, pending_tasks)

    def report(self):
        content = ""
        content += f"Pending : {len(self.current_items)}"
        content += self.ls()[1]
        content += ""
        content += f"Completed : {len(self.completed_items)}"
        for index, task in enumerate(self.completed_items):
            content += f"{index+1}. {task}"
        return (True, content)

    def render_pending_tasks(self):
        self.read_current()
        if len(self.current_items) == 0:
            return "No pending tasks."
        content = """
        <html>
        <head>
            <style>
            table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
            }
            </style>
        </head>
        <body>
            <h1> Pending Tasks </h1>
                <table>
                    <tr>
                        <th>Priority</th>
                        <th>Task</th>
                    </tr>
        """
        for priority in self.current_items:
            content += "<tr>"
            content += f"<td>{priority}</td>"
            content += f"<td>{self.current_items[priority]}</td>"
            content += "</tr>"
        content += "</table></body></html>"
        return content

    def render_completed_tasks(self):
        self.read_completed()
        if len(self.completed_items) == 0:
            return "No completed tasks."
        content = """
        <html>
        <head>
            <style>
            table, td {
                border: 1px solid black;
                border-collapse: collapse;
            }
            </style>
        </head>
        <body>
            <h1> Completed Tasks </h1>
                <table>
                    <tr>
                        <th>Task</th>
                    </tr>
        """
        for task in self.completed_items:
            content += "<tr>"
            content += f"<td>{task}</td>"
            content += "</tr>"
        content += "</table></body></html>"
        return content


class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()
        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())
