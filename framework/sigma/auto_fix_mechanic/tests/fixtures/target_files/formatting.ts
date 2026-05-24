// Fixture: TRAILING-WHITESPACE + MISSING-SEMI (cubiertos por Prettier por default)

export function greet(name: string) {
  const greeting = `Hello, ${name}`
  return greeting
}

export const PI = 3.14
export const E = 2.71

function buildMsg(name: string, age: number) {
  const msg = name + " is " + age
  return msg
}

export default buildMsg
