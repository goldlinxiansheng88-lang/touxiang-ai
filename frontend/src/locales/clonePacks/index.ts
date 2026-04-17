import type { ClonePack } from "./types";

import ar from "./ar";
import de from "./de";
import es from "./es";
import fr from "./fr";
import hi from "./hi";
import id from "./id";
import it from "./it";
import ms from "./ms";
import nl from "./nl";
import pl from "./pl";
import ptBR from "./ptBR";
import ru from "./ru";
import th from "./th";
import tr from "./tr";
import uk from "./uk";
import vi from "./vi";

/** 与 en.base 前台键对齐的完整克隆语言包（16 种） */
export const CLONE_PACKS: Record<string, ClonePack> = {
  es,
  fr,
  de,
  "pt-BR": ptBR,
  ru,
  ar,
  hi,
  id,
  th,
  vi,
  tr,
  pl,
  nl,
  it,
  uk,
  ms,
};
