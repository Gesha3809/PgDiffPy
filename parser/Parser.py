class Parser(object):
    def __init__(self, statement):
        self.position = 0
        self.statement = statement

    # Checks whether the string contains given word on current position. If not
    # then throws an exception.
    def expect(self, *words):
        for word in words:
            self._expect(word, False)

    # Checks whether string contains at current position sequence of the words.
    # Return True if whole sequence was found, raise Exception if first
    # statement was found but other were not found, otherwise False
    def expect_optional(self, *words):
        found = self._expect(words[0], True)

        if not found:
            return False

        for word in words[1:]:
            self.skip_whitespace()
            self._expect(word, False)

        return True

    def parse_identifier(self):
        identifier = self._parse_identifier()

        if self.statement[self.position] == '.':
            self.position += 1
            identifier += '.' + self._parse_identifier()

        self.skip_whitespace()

        return identifier

    def parse_integer(self):
        end_pos = self.position

        while end_pos <= len(self.statement):
            if not self.statement[end_pos].isdigit():
                break
            end_pos += 1

        try:
            result = int(self.statement[self.position: end_pos])

            self.position = end_pos
            self.skip_whitespace()

            return result
        except ValueError:
            raise Exception("Cannot parse string: %s\nExpected integer at position %s '%s'" %
                            (self.statement, self.position + 1, self.statement[self.position: self.position + 20]))

    def parse_data_type(self):
        end_pos = self.position

        while (end_pos < len(self.statement)
                and not self.statement[end_pos].isspace()
                and self.statement[end_pos] not in '(),'):
            end_pos += 1

        if end_pos == self.position:
            raise Exception("Cannot parse string: %s\nExpected data type definition at position %s '%s'" %
                           (self.statement, self.statement + 1, self.statement[self.position: self.position + 20]))

        data_type = self.statement[self.position: end_pos]

        self.position = end_pos
        self.skip_whitespace()

        if ("character" == data_type
                and self.expect_optional("varying")):
            data_type = "character varying"
        elif ("double" == data_type
                and self.expect_optional("precision")):
            data_type = "double precision"

        timestamp = "timestamp" == data_type or "time" == data_type

        if self.statement[self.position] == '(':
            data_type += self.get_expression()

        if timestamp:
            if self.expect_optional("with", "time", "zone"):
                data_type += " with time zone"
            elif self.expect_optional("without", "time", "zone"):
                data_type += " without time zone"

        if self.expect_optional("["):
            self.expect("]")
            data_type += "[]"

        return data_type

    def parse_string(self):
        if self.statement[self.position] == '\'':
            escape = False
            end_pos = self.position + 1

            while end_pos < len(self.statement):
                char = self.statement[end_pos]

                if char == '\\':
                    escape = not escape
                elif not escape and char == '\'':
                    if end_pos + 1 < len(self.statement) and self.statement[end_pos + 1] == '\'':
                        # Treat ''(quote)(quote) as single '(quote) and skip next position
                        end_pos += 1
                    else:
                        break
                end_pos += 1

            result = self.statement[self.position: end_pos + 1]
            # except (final Throwable ex) {
            #     throw new RuntimeException("Failed to get substring: " + string
            #             + " start pos: " + position + " end pos: "
            #             + (endPos + 1), ex);
            # }

            self.position = end_pos + 1
            self.skip_whitespace()

        else:
            end_pos = self.position

            for end_pos in range(end_pos, len(self.statement)):
                char = self.statement[end_pos]

                if char.isspace() or char in ',);':
                    break

            if self.position == end_pos:
                raise Exception("Cannot parse string: %s\nExpected string at position %s" %
                               (self.statement, self.position))

            result = self.statement[self.position: end_pos]

            self.position = end_pos
            self.skip_whitespace()

        return result

    def get_expression(self):
        pos_end = self._get_expression_end()

        if self.position == pos_end:
            raise Exception("Cannot parse string: %s\nExpected expression at position %s '%s'" %
                           (self.statement, self.position + 1, self.statement[self.position:self.position + 20]))

        result = self.statement[self.position:pos_end].strip()

        self.position = pos_end

        return result

    def get_rest(self):
        if self.statement[len(self.statement) - 1] == ';':
            if self.position == len(self.statement) - 1:
                return None
            else:
                result = self.statement[self.position:len(self.statement)-1]
        else:
            result = self.statement[self.position:]

        self.position = len(self.statement)

        return result

    def skip_whitespace(self):
        for self.position in range(self.position, len(self.statement)):
            if not self.statement[self.position].isspace():
                break
            self.position += 1

    def throw_unsupported_command(self):
        raise Exception('Cannot parse string: %s\nUnsupported command at position %s \'%s\'' %
                        (self.statement, self.position + 1, self.statement[self.position: self.position + 20]))

    def _get_expression_end(self):
        braces_count = 0
        single_quote_on = False
        char_pos = self.position

        for char_pos in range(char_pos, len(self.statement)):
            char = self.statement[char_pos]

            if char == '(':
                braces_count += 1
            elif char == ')':
                if braces_count == 0:
                    break
                else:
                    braces_count -= 1
            elif char == '\'':
                single_quote_on = not single_quote_on
            elif (char == ',') and not single_quote_on and (braces_count == 0):
                break
            elif char == ';' and braces_count == 0 and not single_quote_on:
                break

        return char_pos

    def _expect(self, word, is_optional):
        word_end = self.position + len(word)

        if (word_end <= len(self.statement)
            and self.statement[self.position:word_end].lower() == word.lower()
            and (word_end == len(self.statement)
            or self.statement[word_end].isspace()
            or self.statement[word_end] in ';),['
            or word in '(,[]')):
                self.position = word_end
                self.skip_whitespace()
                return True

        if is_optional:
            return False

        # Throw Exception CannotParseStringExpectedWord
        raise Exception('Cannot parse string: %s\nExpected %s at position %s \'%s\'' %
                        (self.statement, word, self.position+1, self.statement[self.position:self.position+20]))

    def _parse_identifier(self):
        quoted = self.statement[self.position] == '"'

        if quoted:
            pos_end = self.statement.find('"', self.position + 1)
            result = self.statement[self.position: pos_end + 1]
            self.position = pos_end + 1

            return result
        else:
            start_pos = self.position

            for self.position in range(start_pos, len(self.statement)):
                char = self.statement[self.position]

                if char.isspace() or char in ',();.':
                    break

            result = self.statement[start_pos:self.position].lower()

            return result


class ParserUtils(object):
    @staticmethod
    def get_schema_name(name, database):
        names = ParserUtils.split_names(name)

        if len(names) < 2:
            return database.default_schema.name
        else:
            return names[0]

    # Returns object name from optionally schema qualified name.
    @staticmethod
    def get_object_name(name):
        names = ParserUtils.split_names(name)

        return names[len(names) - 1]

    @staticmethod
    def get_second_object_name(name):
        names = ParserUtils.split_names(name)

        return names[len(names) - 2]

    @staticmethod
    def get_third_object_name(name):
        names = ParserUtils.split_names(name)

        return names[len(names) - 3] if len(names) >= 3 else None

    @staticmethod
    def split_names(string):
        if string.find('"') == -1:
            return string.split(".")
        else:
            strings = []
            start_pos = 0

            while True:
                if string[start_pos] == '"':
                    end_pos = string.find('"', start_pos + 1)
                    strings.append(string[start_pos + 1:end_pos])

                    if end_pos + 1 == len(string):
                        break
                    elif string[end_pos + 1] == '.':
                        start_pos = end_pos + 2
                    else:
                        start_pos = end_pos + 1
                else:
                    end_pos = string.find('.', start_pos)

                    if end_pos == -1:
                        strings.append(string[start_pos:])
                        break
                    else:
                        strings.append(string[start_pos:end_pos])
                        start_pos = end_pos + 1

            return strings
