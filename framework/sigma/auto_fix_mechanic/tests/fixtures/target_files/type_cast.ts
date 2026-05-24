// Fixture: TYPE-CAST-AS-ANY (as any cuando AST puede resolver tipo)

interface ApiResponse {
  data: { items: number[] };
  status: number;
}

function fetchData(): ApiResponse {
  // TYPE-CAST-AS-ANY violation: literal con shape conocido
  const stub = { data: { items: [1, 2, 3] }, status: 200 } as any;
  return stub;
}

function getItemCount(): number {
  // TYPE-CAST-AS-ANY violation: call con return type conocido
  const response = fetchData() as any;
  return response.data.items.length;
}

// Caso conservador: cast donde inference NO resuelve trivialmente (deberia escalar a C)
function dynamicCast(value: unknown): string {
  return value as any; // edge case: as any sin context inferible
}

export { fetchData, getItemCount, dynamicCast };
