import type { CharacterProfile } from "../../types/scriptGeneration";

type ShortDramaCharacterEditorProps = {
  characters: CharacterProfile[];
  canEditFields?: boolean;
  onUpdateCharacterField?: (
    characterIndex: number,
    field: keyof CharacterProfile,
    value: string,
  ) => void;
};

function renderCharacter(
  character: CharacterProfile,
  index: number,
  canEditFields: boolean,
  onUpdateCharacterField?: (
    characterIndex: number,
    field: keyof CharacterProfile,
    value: string,
  ) => void,
) {
  const canEditCharacter = canEditFields && !!onUpdateCharacterField;

  return (
    <article className="short-script-character" key={`${character.name}-${character.role}`}>
      {canEditCharacter ? (
        <>
          <label className="short-script-edit-field">
            <span>角色姓名</span>
            <input
              data-testid={`character-name-editor-${index}`}
              onChange={(event) => onUpdateCharacterField(index, "name", event.target.value)}
              value={character.name}
            />
          </label>
          <label className="short-script-edit-field">
            <span>角色定位</span>
            <input
              data-testid={`character-role-editor-${index}`}
              onChange={(event) => onUpdateCharacterField(index, "role", event.target.value)}
              value={character.role}
            />
          </label>
          <label className="short-script-edit-field">
            <span>年龄</span>
            <input
              data-testid={`character-age-editor-${index}`}
              onChange={(event) => onUpdateCharacterField(index, "age", event.target.value)}
              value={character.age}
            />
          </label>
          <label className="short-script-edit-field">
            <span>性格 / 人设</span>
            <textarea
              data-testid={`character-personality-editor-${index}`}
              onChange={(event) => onUpdateCharacterField(index, "personality", event.target.value)}
              rows={3}
              value={character.personality}
            />
          </label>
          <label className="short-script-edit-field">
            <span>人物弧光</span>
            <textarea
              data-testid={`character-arc-editor-${index}`}
              onChange={(event) => onUpdateCharacterField(index, "arc", event.target.value)}
              rows={3}
              value={character.arc}
            />
          </label>
        </>
      ) : (
        <>
          <strong>{character.name}</strong>
          <span>{character.role}</span>
          <p>{character.age}</p>
          <p>{character.personality}</p>
          <small>{character.arc}</small>
        </>
      )}
    </article>
  );
}

export function ShortDramaCharacterEditor({
  characters,
  canEditFields = false,
  onUpdateCharacterField,
}: ShortDramaCharacterEditorProps) {
  if (characters.length === 0) {
    return null;
  }

  return (
    <section className="short-script-section">
      <h3>主要人物</h3>
      <div className="short-script-character-grid">
        {characters.map((character, index) =>
          renderCharacter(character, index, canEditFields, onUpdateCharacterField),
        )}
      </div>
    </section>
  );
}
