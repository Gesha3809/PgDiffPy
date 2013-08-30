class Parser(object):
    def __init__(self, statement):
        self.position=0
        self.statement = statement

    # Checks whether the string contains given word on current position. If not
    # then throws an exception.
    def expect(self, *words):
        for word in words:
            self._expect(word, False)

    # Checks whether string contains at current position sequence of the words.
    # Return True if whole sequence was found, raise Exception if first 
    # statement was found but other were not found, otherwise False
    def expectOptional(self, *words):
        found =  self._expect(words[0], True)

        if not found:
            return False

        for word in words[1:]:
            self.skipWhitespace()
            self._expect(word, False)

        return True

    def parseIdentifier(self):
        identifier = self._parseIdentifier()

        if self.statement[self.position] == '.':
            self.position+=1
            identifier += '.' + self._parseIdentifier()

        self.skipWhitespace()

        return identifier

    def parseInteger(self):
        endPos = self.position

        while endPos <= len(self.statement):
            if not self.statement[endPos].isdigit():
                break
            endPos += 1

        try:
            result = int(self.statement[self.position: endPos])

            self.position = endPos
            self.skipWhitespace()

            return result
        except ValueError:
            raise Exception("Cannot parse string: %s\nExpected integer at position %s '%s'" % (self.statement, self.position + 1,
                    self.statement[self.position: self.position + 20]))

    def parseDataType(self):
        endPos = self.position

        while (endPos < len(self.statement)
                and not self.statement[endPos].isspace()
                and self.statement[endPos] not in '(),'):
            endPos += 1

        if (endPos == self.position):
            raise Exception("Cannot parse string: %s\nExpected data type definition at position %s '%s'" % (self.statement, self.statement + 1, self.statement[self.position: self.position + 20]))

        dataType = self.statement[self.position: endPos]

        self.position = endPos
        self.skipWhitespace()

        if ("character" == dataType
                and self.expectOptional("varying")):
            dataType = "character varying"
        elif ("double" == dataType
                and self.expectOptional("precision")):
            dataType = "double precision"

        timestamp = "timestamp" == dataType or "time" == dataType

        if (self.statement[self.position] == '('):
            dataType += self.getExpression()

        if (timestamp):
            if (self.expectOptional("with", "time", "zone")):
                dataType += " with time zone"
            elif (expectOptional("without", "time", "zone")):
                dataType += " without time zone"


        if (self.expectOptional("[")):
            self.expect("]")
            dataType += "[]"

        return dataType

    def parseString(self):
        result = ''
        if (self.statement[self.position] == '\''):
            escape = False
            endPos = self.position + 1

            for endPos in range(endPos, len(self.statement)):
                char = self.statement[endPos]

                if (char == '\\'):
                    escape = not escape
                elif not escape and char == '\'':
                    if (endPos + 1 < len(self.statement) and self.statement[endPos + 1] == '\''):
                        endPos += 1
                    else:
                        break


            result = self.statement[self.position: endPos + 1]
            # except (final Throwable ex) {
            #     throw new RuntimeException("Failed to get substring: " + string
            #             + " start pos: " + position + " end pos: "
            #             + (endPos + 1), ex);
            # }

            self.position = endPos + 1
            self.skipWhitespace()

        else:
            endPos = self.position

            for endPos in range(endPos, len(self.statement)):
                char = self.statement[endPos]

                if (char.isspace() or char in ',);'):
                    break

            if (self.position == endPos):
                raise Exception("Cannot parse string: %s\nExpected string at position %s" % (self.statement, self.position))

            result = self.statement[self.position: endPos]

            self.position = endPos
            self.skipWhitespace()

        return result


    def getExpression(self):
        posEnd = self._getExpressionEnd()

        if (self.position == posEnd):
            raise Exception("Cannot parse string: %s\nExpected expression at position %s '%s'"
                % (self.statement, self.position + 1, self.statement[self.position:self.position + 20]))

        result = self.statement[self.position:posEnd].strip()

        self.position = posEnd

        return result

    def getRest(self):
        if (self.statement[len(self.statement) - 1] == ';'):
            if (self.position == len(self.statement) - 1):
                return None
            else:
                result = self.statement[self.position:len(self.statement)-1]
        else:
            result = self.statement[position:]

        self.position = len(self.statement)

        return result

    def skipWhitespace(self):
        for self.position in range(self.position,len(self.statement)):
            if (not self.statement[self.position].isspace()):
                break
            self.position +=1

    def throwUnsupportedCommand(self):
        raise Exception('Cannot parse string: %s\nUnsupported command at position %s \'%s\'' %
        (self.statement, self.position + 1, self.statement[self.position: self.position + 20]))

    def _getExpressionEnd(self):
        bracesCount = 0
        singleQuoteOn = False
        charPos = self.position

        for charPos in range(charPos, len(self.statement)):
            chr = self.statement[charPos]

            if (chr == '('):
                bracesCount+=1
            elif (chr == ')'):
                if (bracesCount == 0):
                    break
                else:
                    bracesCount-=1
            elif (chr == '\''):
                singleQuoteOn = not singleQuoteOn
            elif ((chr == ',') and not singleQuoteOn and (bracesCount == 0)):
                break
            elif (chr == ';' and bracesCount == 0 and not singleQuoteOn):
                break;

        return charPos

    def _expect(self, word, isoptional):
        wordEnd = self.position + len(word)

        if wordEnd <= len(self.statement):            
            if(self.statement[self.position:wordEnd].lower() == word.lower()):

                #if(wordEnd == len(word) or self.statement[wordEnd].isspace() or self.statement[wordEnd] in ";),[" or word in "(,[]"):
                self.position = wordEnd
                self.skipWhitespace()                
                return True

        if isoptional:
            return False

        # Throw Exception CannotParseStringExpectedWord
        raise Exception('Cannot parse string: %s\nExpected %s at position %s \'%s\''
            % (self.statement, word, self.position+1, self.statement[self.position:self.position+20]))


    def _parseIdentifier(self):
        quoted = self.statement[self.position] == '"'

        if quoted:
            posEnd = self.statement.find('"', self.position + 1)
            result =  self.statement[self.position: posEnd + 1]
            self.position = posEnd + 1

            return result
        else:
            startPos = self.position

            for self.position in range(startPos,len(self.statement)):
                chr = self.statement[self.position]

                if (chr.isspace() or chr in ',();.'):
                    break

            result = self.statement[startPos:self.position].lower()

            return result


class ParserUtils(object):
    @staticmethod
    def getSchemaName(name, database):
        names = ParserUtils.splitNames(name)

        if len(names) < 2:
            return database.defaultSchema.name
        else:
            return names[0]

    # Returns object name from optionally schema qualified name.
    @staticmethod
    def getObjectName(name):
        names = ParserUtils.splitNames(name)

        return names[len(names) - 1]

    @staticmethod
    def getSecondObjectName(name):
        names = ParserUtils.splitNames(name)

        return names[len(names) - 2]

    @staticmethod
    def getThirdObjectName(name):
        names = ParserUtils.splitNames(name)

        return names[len(names) - 3] if len(names) >= 3 else None

    @staticmethod
    def splitNames(string):
        if string.find('"') == -1:
            return string.split(".")
        else:
            strings = []
            startPos = 0

            while True:
                if string[startPos] == '"':
                    endPos = string.find('"', startPos + 1);
                    strings.append(string[startPos + 1:endPos])

                    if endPos + 1 == len(string):
                        break
                    elif string[endPos + 1] == '.':
                        startPos = endPos + 2
                    else:
                        startPos = endPos + 1
                else:
                    endPos = string.find('.', startPos)

                    if endPos == -1:
                        strings.append(string[startPos:])
                        break
                    else:                        
                        strings.append(string[startPos:endPos])
                        startPos = endPos + 1

            return strings
