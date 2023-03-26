const ts = require('typescript');
const fs = require('fs');

function findTopLevelVariable(code, lineNumber) {
  const sourceFile = ts.createSourceFile('temp.ts', code, ts.ScriptTarget.ESNext, true);
  const targetLine = lineNumber - 1;

  for (const statement of sourceFile.statements) {
    // console.log(statement.kind)
    if (ts.SyntaxKind.ExportAssignment === statement.kind || 
      ts.SyntaxKind.VariableStatement === statement.kind || 
      ts.SyntaxKind.FunctionDeclaration === statement.kind || 
      ts.SyntaxKind.ExpressionStatement === statement.kind ||
      ts.SyntaxKind.ClassDeclaration === statement.kind) {
      const startLine = sourceFile.getLineAndCharacterOfPosition(statement.getStart()).line;
      const endLine = sourceFile.getLineAndCharacterOfPosition(statement.getEnd()).line;

      if (startLine <= targetLine && targetLine <= endLine) {
        return code.slice(statement.getStart(), statement.getEnd());
      }
    }
  }

  return null;
}

const args = process.argv.slice(2);
const code = fs.readFileSync(args[0], 'utf-8');
const lineNumber = parseInt(args[1], 10);

console.log(findTopLevelVariable(code, lineNumber));
