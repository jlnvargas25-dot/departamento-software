// Fixture: TS-NON-NULL-ASSERTION (operador x! evitable)

interface User {
  id: string;
  name?: string;
  email?: string;
}

function greet(user: User | null) {
  // TS-NON-NULL-ASSERTION violation: user! deberia ser guard o optional chain
  const id = user!.id;
  // TS-NON-NULL-ASSERTION violation: user!.name!
  const name = user!.name!.toUpperCase();
  return `${name} (${id})`;
}

function getEmail(user: User | undefined): string {
  // TS-NON-NULL-ASSERTION violation
  return user!.email!;
}

export { greet, getEmail };
