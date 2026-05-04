import type { CharacterProfile } from "../../types/scriptGeneration";

type ShortDramaCharacterEditorProps = {
  characters: CharacterProfile[];
};

function renderCharacter(character: CharacterProfile) {
  return (
    <article className="short-script-character" key={`${character.name}-${character.role}`}>
      <strong>{character.name}</strong>
      <span>{character.role}</span>
      <p>{character.age}</p>
      <p>{character.personality}</p>
      <small>{character.arc}</small>
    </article>
  );
}

export function ShortDramaCharacterEditor({ characters }: ShortDramaCharacterEditorProps) {
  if (characters.length === 0) {
    return null;
  }

  return (
    <section className="short-script-section">
      <h3>主要人物</h3>
      <div className="short-script-character-grid">{characters.map(renderCharacter)}</div>
    </section>
  );
}
