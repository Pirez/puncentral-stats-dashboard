


// Steam avatar URLs for each player (local files)
export const playerAvatars: Record<string, string> = {
  'Stutmunn': '/avatars/stutmunn.png',
  'martinsen': '/avatars/martinsen.jpg',
  'Dybbis': '/avatars/dybbis.jpg',
  'nifty': '/avatars/nifty.jpg',
  'Togmannen': '/avatars/togmannen.jpg',
};

export const getPlayerAvatar = (name: string): string | undefined => {
  return playerAvatars[name];
};
