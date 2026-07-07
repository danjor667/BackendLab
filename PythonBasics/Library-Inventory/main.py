import cmd


class Console(cmd.Cmd):
    prompt = '>> '







if __name__ == '__main__':
    Console().cmdloop()