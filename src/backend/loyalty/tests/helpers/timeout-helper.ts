export async function wait(timeout: number): Promise<void> {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve();
    }, timeout);
  });
}